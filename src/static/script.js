document.getElementById('registration-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordConfirmation = document.getElementById('password_confirmation').value;
    const phone = document.getElementById('phone').value;

    if (password !== passwordConfirmation) {
        document.getElementById('message').innerText = 'Паролі не співпадають.';
        return;
    }

    try {
        const response = await fetch('/api/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password,
                password_confirmation: passwordConfirmation,
                phone: phone,
            }),
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('message').innerText = result.detail || 'Реєстрація успішна!';
        } else {
            const error = await response.json();
            document.getElementById('message').innerText = error.detail || 'Сталася помилка.';
        }
    } catch (error) {
        document.getElementById('message').innerText = 'Сталася помилка з мережею.';
    }
});
