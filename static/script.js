document.addEventListener("DOMContentLoaded", () => {
  const textInput = document.getElementById("textInput");
  const imageFile = document.getElementById("imageFile");
  const canvas = document.getElementById("previewCanvas");
  const btn = document.getElementById("btn");
  const receipt = document.getElementById("receipt");
  const statusBox = document.getElementById("status");

  // ---------------- IMAGE PREVIEW ----------------
  imageFile.addEventListener("change", () => {
    const file = imageFile.files[0];
    if (!file) {
      canvas.width = 0;
      canvas.height = 0;
      return;
    }

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onerror = () => {
      statusBox.textContent = "Couldn't load the image — try another one";
      statusBox.classList.remove("hidden");
      canvas.width = 0;
      canvas.height = 0;
    };

    img.onload = () => {
      const W = 384;
      const H = Math.round(img.height * (W / img.width));
      canvas.width = W;
      canvas.height = H;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, W, H);
      ctx.drawImage(img, 0, 0, W, H);
    };
  });

  // ---------------- PRINT ----------------
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    statusBox.classList.remove("hidden");
    statusBox.style.opacity = 1; // reset opacity for fade

    const hasText = textInput.value.trim() !== "";
    const hasImage = imageFile.files.length > 0;

    if (!hasText && !hasImage) {
      statusBox.textContent = "hmm, type something or add an image first!";
      btn.disabled = false;
      return;
    }

    statusBox.textContent = "sending…";

    const form = new FormData();
    form.set("text", textInput.value);
    form.set("has_image", hasImage ? "true" : "false");

    // send canvas image as file (await blob)
    if (hasImage && canvas.width > 0 && canvas.height > 0) {
      const blob = await new Promise(resolve => canvas.toBlob(resolve));
      if (!blob) {
        statusBox.textContent = "Failed to prepare image";
        btn.disabled = false;
        return;
      }
      form.append("image", blob, "preview.png");
    }

    // now send to printer
    const success = await sendToPrinter(form);

    if (success) {
      // show "sent" in the same style as "sent to printer"
      statusBox.textContent = "submission sent!";

      // reset form
      textInput.value = "";
      imageFile.value = "";
      canvas.width = 0;
      canvas.height = 0;

      // optional: brief jolt animation
      receipt.classList.add("jolt-up");
      setTimeout(() => receipt.classList.remove("jolt-up"), 800);

      // fade out message after 2 seconds
      setTimeout(() => {
        statusBox.style.transition = "opacity 1s ease";
        statusBox.style.opacity = 0;
        setTimeout(() => {
          statusBox.classList.add("hidden");
          statusBox.style.transition = "";
        }, 1000);
      }, 2000);
    }

    btn.disabled = false;
  });

  async function sendToPrinter(form) {
    try {
      const res = await fetch("/print", { method: "POST", body: form });
      const msg = await res.text();
      if (res.ok) {
        return true;
      } else {
        statusBox.textContent = msg || "Oops! Something went wrong, goddammit 😅";
        return false;
      }
    } catch (e) {
      statusBox.textContent = "Oops! Something went wrong, goddammit 😅";
      return false;
    }
  }
});
