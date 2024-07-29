document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const startDialogButton = document.getElementById('start-dialog');
    const switchModeButton = document.getElementById('switch-mode');
    const modeControls = document.getElementById('mode-controls');
    const passButton = document.getElementById('pass');
    const takeButton = document.getElementById('take');

    let messages = [];

    const displayMessage = (msg) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', msg.role === 'user' ? 'left' : 'right');

        const usernameElement = document.createElement('span');
        usernameElement.classList.add('username');
        usernameElement.textContent = msg.username;

        const textElement = document.createElement('p');
        textElement.textContent = msg.message;

        const detailsElement = document.createElement('div');
        detailsElement.classList.add('details');

        if (msg.emotion) {
            const emotionElement = document.createElement('div');
            emotionElement.classList.add('emotion');

            const emotionIcon = document.createElement('i');
            emotionIcon.classList.add('fas');
            switch (msg.emotion) {
                case 'грусть':
                    emotionIcon.classList.add('fa-sad-tear');
                    break;
                case 'радость':
                    emotionIcon.classList.add('fa-laugh');
                    break;
                case 'отвращение':
                    emotionIcon.classList.add('fa-frown');
                    break;
                case 'гнев':
                    emotionIcon.classList.add('fa-angry');
                    break;
                case 'страх':
                    emotionIcon.classList.add('fa-flushed');
                    break;
                default:
                    emotionIcon.classList.add('fa-question-circle');
            }

            emotionElement.appendChild(emotionIcon);
            detailsElement.appendChild(emotionElement);
        }

        if (msg.money) {
            const moneyElement = document.createElement('div');
            moneyElement.classList.add('money');

            const moneyIcon = document.createElement('i');
            moneyIcon.classList.add('fas', 'fa-coins');

            moneyElement.textContent = msg.money;
            moneyElement.appendChild(moneyIcon);
            detailsElement.appendChild(moneyElement);
        }

        messageElement.appendChild(usernameElement);
        messageElement.appendChild(textElement);
        messageElement.appendChild(detailsElement);

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight; // Автоматическая прокрутка вниз
    };

    const displayMessagesSequentially = (messages, index = 0) => {
        if (index < messages.length) {
            displayMessage(messages[index]);
            setTimeout(() => displayMessagesSequentially(messages, index + 1), 1000);
        }
    };

    const sendMessagesToServer = async (messages) => {
        try {
            const response = await fetch('/send-messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ messages })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Success:', data);
            await displayMessagesSequentially(data)
            return data
        } catch (error) {
            console.error('Error sending messages:', error);
        }
    };

    const startDialog = async () => {
        try {
            const response = await fetch('/start-dialog', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'start' })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            messages.push(data);
            if (data['action'] == 'Take'){
                await clear_history();
            }
            displayMessagesSequentially(messages);
        } catch (error) {
            console.error('Error starting dialog:', error);
        }
    };
    const clear_history = async () => {
        messages = []
    };
    const switchMode = () => {
        messages = []
        if (modeControls.style.display === 'none') {
            modeControls.style.display = 'block';
            startDialogButton.style.display = 'none';
        } else {
            modeControls.style.display = 'none';
            startDialogButton.style.display = 'block';
        }
    };

    switchModeButton.addEventListener('click', switchMode);

    startDialogButton.addEventListener('click', startDialog);

    passButton.addEventListener('click', async () => {
        const message = {role: 'user', username: 'User', message: 'Pass'};
        messages.push(message);
        displayMessage(message);
        const data = await sendMessagesToServer(messages);
        messages.push(data);
    });

    takeButton.addEventListener('click', async () => {
        const message = {role: 'user', username: 'User', action: 'Take'};
        messages.push(message);
        displayMessage(message);
        const data = await sendMessagesToServer(messages);
        messages.push(data);
        await clear_history();
    });
});
