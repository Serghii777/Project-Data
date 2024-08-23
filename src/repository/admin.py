import csv
from datetime import datetime
from typing import Optional
import uuid
from src.schemas.admin import VehicleCheckSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import BlackListCar, ParkingRate, ParkingRecord, User, Role, Vehicle

async def change_user_status(user: User, is_active: bool, db: AsyncSession):
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)

async def update_user_role(user: User, role: Role, db: AsyncSession):
    user.role = role
    await db.commit()
    await db.refresh(user)

async def set_parking_rate(rate_per_hour: int, max_daily_rate: Optional[int], currency: str, db: AsyncSession):
    new_rate = ParkingRate(
        rate_per_hour=rate_per_hour,
        max_daily_rate=max_daily_rate,
        currency=currency
    )
    db.add(new_rate)
    await db.commit()
    await db.refresh(new_rate)
    return new_rate

async def update_parking_spaces(total_spaces: int, available_spaces: int, db: AsyncSession):
    parking_lot = await db.execute(select(ParkingRate).order_by(ParkingRate.created_at.desc()))
    parking_lot = parking_lot.scalar_one_or_none()
    if parking_lot:
        parking_lot.total_spaces = total_spaces
        parking_lot.available_spaces = available_spaces
        await db.commit()
        await db.refresh(parking_lot)
        return parking_lot
    else:
        new_parking_lot = ParkingRate(
            total_spaces=total_spaces,
            available_spaces=available_spaces
        )
        db.add(new_parking_lot)
        await db.commit()
        await db.refresh(new_parking_lot)
        return new_parking_lot
    

class ParkingRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_parking_record(self, parking_record: ParkingRecord):
        self.db.add(parking_record)
        await self.db.commit()
        await self.db.refresh(parking_record)
        return parking_record

    async def get_parking_duration(self, vehicle_id: uuid.UUID) -> int | None:
        """Повертає тривалість паркування в хвилинах для поточного паркування"""
        result = await self.db.execute(
            select(ParkingRecord)
            .where(ParkingRecord.vehicle_id == vehicle_id)
            .order_by(ParkingRecord.entry_time.desc())
        )
        parking_record = result.scalar_one_or_none()

        if parking_record and parking_record.exit_time:
            duration = (parking_record.exit_time - parking_record.entry_time).total_seconds() // 60
            return int(duration)
        return None
    

async def generate_parking_report(vehicle_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(
        select(ParkingRecord)
        .where(ParkingRecord.vehicle_id == vehicle_id)
        .order_by(ParkingRecord.entry_time)
    )
    
    parking_records = result.scalars().all()
    
    if not parking_records:
        return None
    filename = f"parking_report_{vehicle_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    fields = ['Час в’їзду', 'Час виїзду', 'Тривалість (хв)', 'Вартість (грн)']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for record in parking_records:
            csvwriter.writerow([record.entry_time, record.exit_time, record.duration, record.cost])
    
    return filename


class ParkingRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_vehicle_to_parking(self, vehicle_check: VehicleCheckSchema) -> ParkingRecord:
        result = await self.db.execute(
            select(BlackListCar).where(BlackListCar.token == vehicle_check.license_plate)
        )
        blacklisted = result.scalar_one_or_none()
        if blacklisted:
            raise ValueError("Vehicle is blacklisted.")
        result = await self.db.execute(
            select(Vehicle).where(Vehicle.license_plate == vehicle_check.license_plate)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise ValueError("Vehicle not found.")
        parking_record = ParkingRecord(
            vehicle_id=vehicle.id,
            entry_time=datetime.now()
        )

        self.db.add(parking_record)
        await self.db.commit()
        await self.db.refresh(parking_record)

        return parking_record
    
    async def end_parking_by_license_plate(self, license_plate: str) -> ParkingRecord:
        result = await self.db.execute(
            select(Vehicle).where(Vehicle.license_plate == license_plate)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise ValueError("Vehicle not found.")
        result = await self.db.execute(
            select(ParkingRecord)
            .where(ParkingRecord.vehicle_id == vehicle.id)
            .order_by(ParkingRecord.entry_time.desc())
        )
        parking_record = result.scalar_one_or_none()

        if not parking_record:
            raise ValueError("No parking record found for this vehicle.")

        # Завершити паркування
        parking_record.exit_time = datetime.now()
        if parking_record.entry_time:
            duration = (parking_record.exit_time - parking_record.entry_time).total_seconds() // 60
            parking_record.duration = int(duration)
            parking_record.cost = await self.calculate_cost(parking_record.duration)
        
        self.db.add(parking_record)
        await self.db.commit()
        await self.db.refresh(parking_record)
        return parking_record
    
    async def calculate_cost(self, duration: int) -> int:
        rate_per_hour, max_daily_rate = await self.get_parking_rates()
        total_hours = (duration + 59) // 60  
        cost = total_hours * rate_per_hour
        if max_daily_rate is not None:
            cost = min(cost, max_daily_rate)
        
        return cost
    
    async def get_parking_rates(self) -> tuple[int, int]:
        async with self.db.begin():
            query = select(ParkingRate).order_by(ParkingRate.id.desc()).limit(1)
            result = await self.db.execute(query)
            parking_rate = result.scalar_one_or_none()
            
            if parking_rate:
                return parking_rate.rate_per_hour, parking_rate.max_daily_rate
            else:
                raise Exception("Parking rate information is not available")


        

class BlackListRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_to_blacklist(self, license_plate: str):
        blacklisted_entry = BlackListCar(license_plate=license_plate)
        self.db.add(blacklisted_entry)
        await self.db.commit()
        return blacklisted_entry

    async def is_blacklisted(self, license_plate: str) -> bool:
        query = select(BlackListCar).where(BlackListCar.license_plate == license_plate)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None