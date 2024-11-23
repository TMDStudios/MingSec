const imageElement = document.querySelector('.screencap img');
const instructions = document.getElementById("instructions");
const prevArrow = document.querySelector('.prev');
const nextArrow = document.querySelector('.next');

const instructionsText = [
    "MingSec requires you to be logged in to interact with the security system.",
    "Once logged in, you can send camera requests to the security system and view log files that have been uploaded to Dropbox. Each time a 'status' request has been made, a log file is uploaded to dropbox.",
    "This is what the security system displays once activated in GitBash. The running log is uploaded to Dropbox when a 'status' report is requested.",
    "This is what a successfully sent camera request looks like.",
    "Any time the alarm is tripped, a notification is sent to your phone. Opening the app also allows you to view all logged alarms.",
    "A triggered alarm uploads an image to Dropbox and records a video that is then also uploaded to Dropbox. If the internet is down, the system waits until a connection is reestablished and then uploads the images/videos."
];

let currentIndex = 1;
const totalImages = 6;

let intervalId;

function updateImage() {
    imageElement.src = `media/${currentIndex}.png`;
    instructions.innerHTML = instructionsText[currentIndex - 1];
}

function nextImg() {
    currentIndex = currentIndex < totalImages ? currentIndex + 1 : 1;
    updateImage();
}

function prevImg() {
    currentIndex = currentIndex > 1 ? currentIndex - 1 : totalImages;
    updateImage();
}

function startAutoCycle() {
    intervalId = setInterval(nextImg, 5000);
}

function stopAutoCycle() {
    clearInterval(intervalId);
}

[instructions, imageElement, prevArrow, nextArrow].forEach(element => {
    element.addEventListener('mouseenter', stopAutoCycle);
    element.addEventListener('mouseleave', startAutoCycle);
});

updateImage();
startAutoCycle();