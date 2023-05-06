
let email;
const video = document.querySelector('video');
const loginBtn = document.querySelector('button#login');
const canvas = document.createElement('canvas');
const emailCheckpoint = document.querySelector(".email-checkpoint-btn");
const counter = document.querySelector(".counter-overlay");
const floatMsg = document.querySelector(".float-msg");
const errorCloseBtn = floatMsg.querySelector(".error-close");

errorCloseBtn.addEventListener("click", () => {
    floatMsg.classList.remove("show")
})

function showError(text) {
    const errorMsg = floatMsg.querySelector(".error-msg");
    errorMsg.textContent = text
    floatMsg.classList.add("show")
    const showMsgInterval = setTimeout(() => {
        floatMsg.classList.remove("show")
    }, 5000)
} 



async function callAPI(url = "/", method = "GET", body = {}) {
    return await fetch(url, {
        method: method,
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
        },
        redirect: "follow",
        referrerPolicy: "no-referrer",
        body: JSON.stringify(body),
    });
}

emailCheckpoint.addEventListener("click", async () => {
    const emailInput = document.querySelector(".email-checkpoint #email")
    if (emailInput.value != "") {

        let url = "http://127.0.0.1:5000/face-id/checkpoint/email";
        const response = await callAPI(url, "POST", {"email": emailInput.value})
        let { result } = await response.json()
        if (result === "Already exist") {
            email = emailInput.value;
            const form = document.querySelector(".float-form")
            form.classList.toggle("float")

            await openWebcam()

        } else {
            await showError("Email not exists yet, please register a new account!");
            emailInput.value = ""
            emailInput.focus()
        }
    } else {
        await showError("Email is required!")
    }

});

const webcamOnEvent = new Event('webcamOn');

// Đăng ký lắng nghe sự kiện tùy chỉnh "webcamOn"
document.addEventListener('webcamOn', () => {
    loginBtn.removeAttribute("disabled");
});

async function openWebcam() {
    return navigator.mediaDevices.getUserMedia({ audio: false, video: true })
        .then(stream => {
            video.srcObject = stream
            document.dispatchEvent(webcamOnEvent);
        })    
        .catch (error => console.error(error));
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function takePicture() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    let url = canvas.toDataURL("image/png");
    let compressedImage = await compressDataURL(url, 0.92)
    compressedImage = compressedImage.replace(/^data:image\/(png|jpg);base64,/, "");

    return compressedImage

};

function compressDataURL(dataURL, quality) {
    return new Promise((resolve, reject) => {
        var img = new Image();
        img.src = dataURL;
        img.onload = function () {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var width = img.width;
            var height = img.height;
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);
            var compressedDataURL = canvas.toDataURL('image/png', quality);
            resolve(compressedDataURL);
        };
        img.onerror = reject;
    });
}

async function login(body = {}) {
    let url = "http://127.0.0.1:5000/face-id/login";
    const response = await callAPI(url, "POST", body)
    return response.json();
}

async function handleLogin() {
    let loader = document.querySelector(".loader")
    loader.style.display = "block";

    let image = await takePicture()
    let response = await login({
        "email": email,
        "image": image
    })

    console.log(response);
    let { face_founded, matched, fake } = response;

    if (fake) {
        await showError("Cannot use an image to login!") 
    } else if (!face_founded) {
        await showError("No face founded")
    } else if (matched) {
        window.location.href = "http://127.0.0.1:5500/client/home.html";
        return
    } else {
        await showError("Login failed, please try again!")
    }
    counter.textContent = 3;
    loader.style.display = "none";
    loginBtn.removeAttribute("disabled");

}

loginBtn.addEventListener('click', async () => {
    counter.style.display = "block";
    loginBtn.setAttribute("disabled", true)
    startTimer(3, counter);
});

function startTimer(duration, element) {

    const idInterval = setInterval(async function () {

        element.textContent = duration;

        if (--duration < 0) {
            clearInterval(idInterval)
            element.style.display = "none";
            handleLogin();
        }
    }, 1000);
}