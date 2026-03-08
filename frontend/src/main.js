import JSZip from "jszip";

const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('InputButton');
const preview = document.getElementById('preview');

const BACKEND_URL = "http://127.0.0.1:8000"; // поменяй если другой порт

fileInput.addEventListener('change', function () {
    preview.innerHTML = "";

    const files = this.files;

    for (let file of files) {

        const reader = new FileReader();

        reader.onload = function (e) {

            const img = document.createElement("img");
            img.src = e.target.result;
            img.style.width = "150px";
            img.style.margin = "10px";

            preview.appendChild(img);
        };

        reader.readAsDataURL(file);
    }
});


form.addEventListener('submit', async (e) => {
    console.log("event submit")
    e.preventDefault();

    if (!fileInput.files.length) {
        alert('Пожалуйста, загрузите изображения!');
        return;
    }

    const zip = new JSZip();
    const files = fileInput.files;

    for (let file of files) {
        zip.file(file.name, file);
    }

    const zipBlob = await zip.generateAsync({ type: "blob" });
    console.log(zipBlob)

    const formData = new FormData();
    formData.append("file", zipBlob, "images.zip");

    const response = await fetch(`${BACKEND_URL}/upload-zip`, {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    preview.innerHTML = "";

    for (let res of data.results) {

        const block = document.createElement("div");
        block.style.margin = "20px";

        const img = document.createElement("img");
        img.src = `${BACKEND_URL}/${res.image_url}`;

        const caption = document.createElement("pre");

        const txtResponse = await fetch(`${BACKEND_URL}/${res.txt_url}`);
        const text = await txtResponse.text();

        caption.textContent = text;

        block.appendChild(img);
        block.appendChild(caption);

        preview.appendChild(block);
    }

});
