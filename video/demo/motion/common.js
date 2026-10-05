// Shared helpers. Every animation is a pure function of time t (seconds), so any frame
// can be rendered in any order and the result is identical every run.
const clamp = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => x * x * x * (x * (6 * x - 15) + 10); // smootherstep

// Slow push-in across the whole shot, like a camera dolly.
function stagePush(progress) {
  document.getElementById("stage").style.transform = `scale(${1 + 0.035 * progress})`;
}

// Film grain from a seeded generator: random-looking, but the same for the same frame.
function grain(t) {
  const canvas = document.getElementById("grain");
  const ctx = canvas.getContext("2d");
  const img = ctx.createImageData(canvas.width, canvas.height);
  let seed = Math.floor(t * 24) * 7919 + 17;
  const rand = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < img.data.length; i += 4) {
    const v = 128 + (rand() - 0.5) * 120;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}
