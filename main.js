import { SignalGenerator, FFTUtils } from './dsp.js';

// --- State Management ---
const state = {
    visualizer: {
        signalType: 'sine',
        frequency: 5,
        amplitude: 1,
        phase: 0,
        samplingRate: 1000,
        noiseLevel: 0,
        filterType: 'none'
    },
    playground: {
        isRunning: false,
        signalType: 'sine',
        frequency: 5,
        amplitude: 1,
        buffer: []
    },
    experiments: {
        selectedKernel: 'Gaussian Blur',
        kernelScale: 1,
        kernels: {
            'Gaussian Blur': [0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05],
            'Edge Detection': [-1, -1, -1, 8, -1, -1, -1],
            'Smoothing': [0.2, 0.2, 0.2, 0.2, 0.2],
            'Sharpening': [0, -1, 0, -1, 5, -1, 0, -1, 0]
        }
    }
};

// --- Charts Initialization ---
let timeChart, freqChart, convChart;

function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
            x: { grid: { color: 'rgba(0, 255, 65, 0.1)' }, ticks: { color: 'rgba(0, 255, 65, 0.5)' } },
            y: { grid: { color: 'rgba(0, 255, 65, 0.1)' }, ticks: { color: 'rgba(0, 255, 65, 0.5)' } }
        },
        plugins: { legend: { display: false } }
    };

    timeChart = new Chart(document.getElementById('timeChart'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: 'Original', borderColor: '#00ff41', borderWidth: 2, data: [], pointRadius: 0 },
            { label: 'Filtered', borderColor: '#ff8c00', borderWidth: 2, data: [], pointRadius: 0 }
        ]},
        options: commonOptions
    });

    freqChart = new Chart(document.getElementById('freqChart'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: 'Magnitude', borderColor: '#00d4ff', borderWidth: 2, data: [], pointRadius: 0 }
        ]},
        options: { ...commonOptions, scales: { 
            x: { ...commonOptions.scales.x, ticks: { color: 'rgba(0, 212, 255, 0.5)' } },
            y: { ...commonOptions.scales.y, ticks: { color: 'rgba(0, 212, 255, 0.5)' }, title: { display: true, text: 'dB', color: '#00d4ff' } }
        }}
    });

    convChart = new Chart(document.getElementById('convChart'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: 'Original', borderColor: 'rgba(0, 255, 65, 0.6)', borderWidth: 2, data: [], pointRadius: 0 },
            { label: 'Convolved', borderColor: '#00d4ff', borderWidth: 2, data: [], pointRadius: 0 }
        ]},
        options: commonOptions
    });
}

// --- Update Functions ---
function updateVisualizer() {
    const params = {
        frequency: state.visualizer.frequency,
        amplitude: state.visualizer.amplitude,
        phase: state.visualizer.phase,
        samplingRate: state.visualizer.samplingRate,
        duration: 2,
        noiseLevel: state.visualizer.noiseLevel
    };

    let signal;
    switch(state.visualizer.signalType) {
        case 'sine': signal = SignalGenerator.generateSineWave(params); break;
        case 'square': signal = SignalGenerator.generateSquareWave(params); break;
        case 'triangle': signal = SignalGenerator.generateTriangleWave(params); break;
        case 'noise': signal = SignalGenerator.generateNoiseSignal(params); break;
    }

    let filtered = signal.amplitude;
    if (state.visualizer.filterType === 'lowpass') {
        filtered = SignalGenerator.applyLowPassFilter(signal.amplitude, 5);
    } else if (state.visualizer.filterType === 'highpass') {
        filtered = SignalGenerator.applyHighPassFilter(signal.amplitude, 5);
    }

    // Update Time Chart
    const displayCount = 500;
    timeChart.data.labels = signal.time.slice(0, displayCount).map(t => t.toFixed(3));
    timeChart.data.datasets[0].data = signal.amplitude.slice(0, displayCount);
    timeChart.data.datasets[1].data = state.visualizer.filterType !== 'none' ? filtered.slice(0, displayCount) : [];
    timeChart.update();

    // Update Frequency Chart
    const fft = FFTUtils.computeFFT(signal.amplitude);
    const dbMagnitude = FFTUtils.magnitudeToDb(fft.magnitude);
    const freqAxis = fft.frequency.map(f => (f * state.visualizer.samplingRate).toFixed(1));
    
    freqChart.data.labels = freqAxis.slice(0, 256);
    freqChart.data.datasets[0].data = dbMagnitude.slice(0, 256);
    freqChart.update();

    // Update Analysis
    updateAnalysis(signal.amplitude);
}

function updateAnalysis(signal) {
    const peak = Math.max(...signal.map(Math.abs));
    const mean = signal.reduce((a, b) => a + b, 0) / signal.length;
    const rms = Math.sqrt(signal.reduce((a, b) => a + b * b, 0) / signal.length);
    const crest = rms !== 0 ? peak / rms : 0;

    document.getElementById('stat-peak').textContent = peak.toFixed(2);
    document.getElementById('stat-rms').textContent = rms.toFixed(2);
    document.getElementById('stat-mean').textContent = mean.toFixed(2);
    document.getElementById('stat-crest').textContent = crest.toFixed(2);
}

function updateExperiments() {
    const params = {
        frequency: 5,
        amplitude: 1,
        phase: 0,
        samplingRate: 1000,
        duration: 2,
        noiseLevel: 0.1
    };

    const signal = SignalGenerator.generateSineWave(params);
    const kernel = state.experiments.kernels[state.experiments.selectedKernel].map(v => v * state.experiments.kernelScale);
    const convolved = SignalGenerator.applyConvolution(signal.amplitude, kernel);

    const displayCount = 500;
    convChart.data.labels = signal.time.slice(0, displayCount).map(t => t.toFixed(3));
    convChart.data.datasets[0].data = signal.amplitude.slice(0, displayCount);
    convChart.data.datasets[1].data = convolved.slice(0, displayCount);
    convChart.update();

    // Update Kernel Display
    document.getElementById('kernel-name').textContent = state.experiments.selectedKernel;
    const valuesDisplay = document.getElementById('kernel-values-display');
    valuesDisplay.innerHTML = '';
    kernel.forEach(v => {
        const span = document.createElement('span');
        span.textContent = v.toFixed(2);
        valuesDisplay.appendChild(span);
    });
}

// --- Playground Animation ---
const pgCanvas = document.getElementById('playgroundCanvas');
const pgCtx = pgCanvas.getContext('2d');
let pgAnimationId;

function drawPlayground() {
    const width = pgCanvas.width;
    const height = pgCanvas.height;
    const centerY = height / 2;

    pgCtx.fillStyle = "#0a0e27";
    pgCtx.fillRect(0, 0, width, height);

    // Grid
    pgCtx.strokeStyle = "rgba(0, 255, 65, 0.1)";
    pgCtx.lineWidth = 1;
    for (let i = 0; i < width; i += 50) { pgCtx.beginPath(); pgCtx.moveTo(i, 0); pgCtx.lineTo(i, height); pgCtx.stroke(); }
    for (let i = 0; i < height; i += 50) { pgCtx.beginPath(); pgCtx.moveTo(0, i); pgCtx.lineTo(width, i); pgCtx.stroke(); }

    // Center line
    pgCtx.strokeStyle = "rgba(0, 255, 65, 0.3)";
    pgCtx.beginPath(); pgCtx.moveTo(0, centerY); pgCtx.lineTo(width, centerY); pgCtx.stroke();

    // Waveform
    if (state.playground.buffer.length > 1) {
        pgCtx.strokeStyle = "rgba(0, 255, 65, 0.2)";
        pgCtx.lineWidth = 8;
        pgCtx.beginPath();
        pgCtx.moveTo(0, centerY - state.playground.buffer[0] * (height / 4));
        for (let i = 1; i < Math.min(state.playground.buffer.length, width); i++) {
            pgCtx.lineTo(i, centerY - state.playground.buffer[i] * (height / 4));
        }
        pgCtx.stroke();

        pgCtx.strokeStyle = "rgba(0, 255, 65, 1)";
        pgCtx.lineWidth = 2;
        pgCtx.beginPath();
        pgCtx.moveTo(0, centerY - state.playground.buffer[0] * (height / 4));
        for (let i = 1; i < Math.min(state.playground.buffer.length, width); i++) {
            pgCtx.lineTo(i, centerY - state.playground.buffer[i] * (height / 4));
        }
        pgCtx.stroke();
    }

    // Labels
    pgCtx.fillStyle = "rgba(0, 255, 65, 0.7)";
    pgCtx.font = "12px 'JetBrains Mono'";
    pgCtx.fillText(`Freq: ${state.playground.frequency.toFixed(1)} Hz`, 10, 20);
    pgCtx.fillText(`Amp: ${state.playground.amplitude.toFixed(2)}`, 10, 35);
    pgCtx.fillText(state.playground.signalType.toUpperCase(), 10, 50);
}

function animatePlayground() {
    if (!state.playground.isRunning) return;

    const params = {
        frequency: state.playground.frequency,
        amplitude: state.playground.amplitude,
        phase: 0,
        samplingRate: 1000,
        duration: 0.1, // Generate in small chunks
        noiseLevel: 0
    };

    let newData;
    switch(state.playground.signalType) {
        case 'sine': newData = SignalGenerator.generateSineWave(params).amplitude; break;
        case 'square': newData = SignalGenerator.generateSquareWave(params).amplitude; break;
        case 'triangle': newData = SignalGenerator.generateTriangleWave(params).amplitude; break;
    }

    state.playground.buffer = [...state.playground.buffer, ...newData];
    if (state.playground.buffer.length > 2000) {
        state.playground.buffer = state.playground.buffer.slice(-2000);
    }

    drawPlayground();
    pgAnimationId = requestAnimationFrame(animatePlayground);
}

// --- Event Listeners ---
function setupEventListeners() {
    // Main Tabs
    document.querySelectorAll('.tab-trigger').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-trigger').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
            if (btn.dataset.tab === 'experiments') updateExperiments();
        });
    });

    // Sub Tabs (Visualizer)
    document.querySelectorAll('.sub-tab-trigger').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.sub-tab-trigger').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.sub-tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.subtab + '-view').classList.add('active');
        });
    });

    // Exp Tabs
    document.querySelectorAll('.exp-tab-trigger').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.exp-tab-trigger').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.exp-tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.exptab + '-view').classList.add('active');
        });
    });

    // Visualizer Controls
    document.querySelectorAll('#signal-type-group .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#signal-type-group .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.visualizer.signalType = btn.dataset.type;
            updateVisualizer();
        });
    });

    document.getElementById('freq-slider').addEventListener('input', (e) => {
        state.visualizer.frequency = parseFloat(e.target.value);
        document.getElementById('freq-val').textContent = state.visualizer.frequency.toFixed(1) + ' Hz';
        updateVisualizer();
    });

    document.getElementById('amp-slider').addEventListener('input', (e) => {
        state.visualizer.amplitude = parseFloat(e.target.value);
        document.getElementById('amp-val').textContent = state.visualizer.amplitude.toFixed(2);
        updateVisualizer();
    });

    document.getElementById('phase-slider').addEventListener('input', (e) => {
        state.visualizer.phase = parseFloat(e.target.value);
        document.getElementById('phase-val').textContent = state.visualizer.phase.toFixed(2) + ' rad';
        updateVisualizer();
    });

    document.getElementById('sr-slider').addEventListener('input', (e) => {
        state.visualizer.samplingRate = parseInt(e.target.value);
        document.getElementById('sr-val').textContent = state.visualizer.samplingRate + ' Hz';
        updateVisualizer();
    });

    document.getElementById('noise-slider').addEventListener('input', (e) => {
        state.visualizer.noiseLevel = parseFloat(e.target.value);
        document.getElementById('noise-val').textContent = (state.visualizer.noiseLevel * 100).toFixed(0) + '%';
        updateVisualizer();
    });

    document.querySelectorAll('#filter-type-group .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#filter-type-group .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.visualizer.filterType = btn.dataset.filter;
            updateVisualizer();
        });
    });

    // Playground Controls
    document.querySelectorAll('#pg-type-group .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#pg-type-group .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.playground.signalType = btn.dataset.type;
        });
    });

    document.getElementById('pg-freq-slider').addEventListener('input', (e) => {
        state.playground.frequency = parseFloat(e.target.value);
        document.getElementById('pg-freq-val').textContent = state.playground.frequency.toFixed(1) + ' Hz';
    });

    document.getElementById('pg-amp-slider').addEventListener('input', (e) => {
        state.playground.amplitude = parseFloat(e.target.value);
        document.getElementById('pg-amp-val').textContent = state.playground.amplitude.toFixed(2);
    });

    document.getElementById('pg-play-btn').addEventListener('click', (e) => {
        state.playground.isRunning = !state.playground.isRunning;
        e.target.textContent = state.playground.isRunning ? '⏸ Pause' : '▶ Play';
        if (state.playground.isRunning) animatePlayground();
    });

    document.getElementById('pg-reset-btn').addEventListener('click', () => {
        state.playground.buffer = [];
        drawPlayground();
    });

    // Experiment Controls
    document.querySelectorAll('#kernel-selector .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#kernel-selector .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.experiments.selectedKernel = btn.dataset.kernel;
            updateExperiments();
        });
    });

    document.getElementById('kernel-scale-slider').addEventListener('input', (e) => {
        state.experiments.kernelScale = parseFloat(e.target.value);
        document.getElementById('kernel-scale-val').textContent = state.experiments.kernelScale.toFixed(2);
        updateExperiments();
    });
}

// --- Initialization ---
window.addEventListener('DOMContentLoaded', () => {
    initCharts();
    setupEventListeners();
    updateVisualizer();
    drawPlayground();
});
