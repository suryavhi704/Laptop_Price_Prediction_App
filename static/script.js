document.addEventListener('DOMContentLoaded', () => {

  const els = {
    company: document.getElementById('company'),
    type: document.getElementById('type'),
    ram: document.getElementById('ram'),
    weight: document.getElementById('weight'),
    screenSize: document.getElementById('screen_size'),
    resolution: document.getElementById('resolution'),
    cpu: document.getElementById('cpu'),
    gpu: document.getElementById('gpu'),
    hdd: document.getElementById('hdd'),
    ssd: document.getElementById('ssd'),
    os: document.getElementById('os'),
  };

  const spec = {
    company: document.getElementById('spec-company'),
    type: document.getElementById('spec-type'),
    ram: document.getElementById('spec-ram'),
    weight: document.getElementById('spec-weight'),
    touchscreen: document.getElementById('spec-touchscreen'),
    ips: document.getElementById('spec-ips'),
    display: document.getElementById('spec-display'),
    ppi: document.getElementById('spec-ppi'),
    cpu: document.getElementById('spec-cpu'),
    gpu: document.getElementById('spec-gpu'),
    storage: document.getElementById('spec-storage'),
    os: document.getElementById('spec-os'),
  };

  const screenReadout = document.getElementById('screen_size_readout');
  const priceValueEl = document.getElementById('price-value');
  const estimateBtn = document.getElementById('estimate-btn');
  const errorMsg = document.getElementById('error-msg');

  const toggleState = { touchscreen: 'Yes', ips: 'Yes' };

  function calcPPI() {
    const [x, y] = els.resolution.value.split('x').map(Number);
    const size = parseFloat(els.screenSize.value) || 13;
    return Math.sqrt(x ** 2 + y ** 2) / size;
  }

  function updateSpecSheet() {
    spec.company.textContent = els.company.value;
    spec.type.textContent = els.type.value;
    spec.ram.textContent = `${els.ram.value} GB`;
    spec.weight.textContent = `${parseFloat(els.weight.value || 0).toFixed(2)} kg`;
    spec.touchscreen.textContent = toggleState.touchscreen;
    spec.ips.textContent = toggleState.ips;
    spec.display.textContent = `${parseFloat(els.screenSize.value).toFixed(1)}" · ${els.resolution.value}`;
    spec.ppi.textContent = `${calcPPI().toFixed(1)} ppi`;
    spec.cpu.textContent = els.cpu.value;
    spec.gpu.textContent = els.gpu.value;

    const hdd = parseInt(els.hdd.value, 10);
    const ssd = parseInt(els.ssd.value, 10);
    const storageParts = [];
    if (ssd > 0) storageParts.push(`${ssd} GB SSD`);
    if (hdd > 0) storageParts.push(`${hdd} GB HDD`);
    spec.storage.textContent = storageParts.length ? storageParts.join(' + ') : 'None';

    spec.os.textContent = els.os.value;

    screenReadout.textContent = `${parseFloat(els.screenSize.value).toFixed(1)}"`;
  }

  Object.values(els).forEach((el) => {
    el.addEventListener('input', updateSpecSheet);
    el.addEventListener('change', updateSpecSheet);
  });

  document.querySelectorAll('.segmented').forEach((group) => {
    const key = group.dataset.target;
    group.querySelectorAll('.seg-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.seg-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        toggleState[key] = btn.dataset.value;
        updateSpecSheet();
      });
    });
  });

  function setPrice(html) {
    priceValueEl.classList.remove('filled');
    // Force reflow so the reveal animation replays on every update.
    void priceValueEl.offsetWidth;
    priceValueEl.innerHTML = html;
    priceValueEl.classList.add('filled');
  }

  async function estimatePrice() {
    errorMsg.textContent = '';
    estimateBtn.classList.add('loading');
    estimateBtn.textContent = 'Estimating…';

    const payload = {
      company: els.company.value,
      type: els.type.value,
      ram: els.ram.value,
      weight: els.weight.value,
      touchscreen: toggleState.touchscreen,
      ips: toggleState.ips,
      screen_size: els.screenSize.value,
      resolution: els.resolution.value,
      cpu: els.cpu.value,
      hdd: els.hdd.value,
      ssd: els.ssd.value,
      gpu: els.gpu.value,
      os: els.os.value,
    };

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Could not estimate the price.');
      }

      const formatted = new Intl.NumberFormat('en-IN').format(data.price);
      setPrice(`&#8377;${formatted}`);
    } catch (err) {
      errorMsg.textContent = err.message;
    } finally {
      estimateBtn.classList.remove('loading');
      estimateBtn.textContent = 'Estimate price';
    }
  }

  estimateBtn.addEventListener('click', estimatePrice);

  updateSpecSheet();
});
