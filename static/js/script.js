document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const startDialogButton = document.getElementById('start-dialog');

    const displayMessage = (msg) => {
        const messageElement = document.createElement('div');
        // Добавляем классы в зависимости от роли сообщения
        if (msg.role === 'user') {
            messageElement.classList.add('message', 'left');
        } else {
            messageElement.classList.add('message', 'right');
        }

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
    };

    const displayMessagesSequentially = (messages, index = 0) => {
        if (index < messages.length) {
            displayMessage(messages[index]);
            setTimeout(() => displayMessagesSequentially(messages, index + 1), 1000);
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
            displayMessagesSequentially(data);
        } catch (error) {
            console.error('Error starting dialog:', error);
        }
    };

    startDialogButton.addEventListener('click', startDialog);
});
