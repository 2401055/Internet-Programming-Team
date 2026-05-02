/**
 * DSP Library for Signal Visualization Platform
 * Ported from original TypeScript implementation
 */

export const SignalGenerator = {
  generateSineWave(params) {
    const { frequency, amplitude, phase, samplingRate, duration, noiseLevel } = params;
    const samples = Math.floor(samplingRate * duration);
    const time = [];
    const amplitudes = [];

    for (let i = 0; i < samples; i++) {
      const t = i / samplingRate;
      time.push(t);
      const signal = amplitude * Math.sin(2 * Math.PI * frequency * t + phase);
      const noise = (Math.random() - 0.5) * 2 * noiseLevel;
      amplitudes.push(signal + noise);
    }
    return { time, amplitude: amplitudes };
  },

  generateSquareWave(params) {
    const { frequency, amplitude, phase, samplingRate, duration, noiseLevel } = params;
    const samples = Math.floor(samplingRate * duration);
    const time = [];
    const amplitudes = [];

    for (let i = 0; i < samples; i++) {
      const t = i / samplingRate;
      time.push(t);
      const normalizedTime = (2 * frequency * t + phase / (2 * Math.PI)) % 1;
      const signal = normalizedTime < 0.5 ? amplitude : -amplitude;
      const noise = (Math.random() - 0.5) * 2 * noiseLevel;
      amplitudes.push(signal + noise);
    }
    return { time, amplitude: amplitudes };
  },

  generateTriangleWave(params) {
    const { frequency, amplitude, phase, samplingRate, duration, noiseLevel } = params;
    const samples = Math.floor(samplingRate * duration);
    const time = [];
    const amplitudes = [];

    for (let i = 0; i < samples; i++) {
      const t = i / samplingRate;
      time.push(t);
      const period = 1 / frequency;
      const normalizedTime = ((2 * frequency * t + phase / (2 * Math.PI)) % 1) * period;
      let signal;
      if (normalizedTime < period / 2) {
        signal = (4 * amplitude / period) * normalizedTime - amplitude;
      } else {
        signal = amplitude - (4 * amplitude / period) * (normalizedTime - period / 2);
      }
      const noise = (Math.random() - 0.5) * 2 * noiseLevel;
      amplitudes.push(signal + noise);
    }
    return { time, amplitude: amplitudes };
  },

  generateNoiseSignal(params) {
    const { amplitude, samplingRate, duration, noiseLevel } = params;
    const samples = Math.floor(samplingRate * duration);
    const time = [];
    const amplitudes = [];

    for (let i = 0; i < samples; i++) {
      const t = i / samplingRate;
      time.push(t);
      const noise = (Math.random() - 0.5) * 2 * amplitude * noiseLevel;
      amplitudes.push(noise);
    }
    return { time, amplitude: amplitudes };
  },

  applyLowPassFilter(signal, windowSize = 5) {
    const filtered = [];
    const halfWindow = Math.floor(windowSize / 2);
    for (let i = 0; i < signal.length; i++) {
      let sum = 0, count = 0;
      for (let j = -halfWindow; j <= halfWindow; j++) {
        const idx = i + j;
        if (idx >= 0 && idx < signal.length) {
          sum += signal[idx];
          count++;
        }
      }
      filtered.push(sum / count);
    }
    return filtered;
  },

  applyHighPassFilter(signal, windowSize = 5) {
    const filtered = [];
    const halfWindow = Math.floor(windowSize / 2);
    for (let i = 0; i < signal.length; i++) {
      const original = signal[i];
      let lowPassValue = 0, count = 0;
      for (let j = -halfWindow; j <= halfWindow; j++) {
        const idx = i + j;
        if (idx >= 0 && idx < signal.length) {
          lowPassValue += signal[idx];
          count++;
        }
      }
      filtered.push(original - lowPassValue / count);
    }
    return filtered;
  },

  applyConvolution(signal, kernel) {
    const result = [];
    const kernelSize = kernel.length;
    const halfKernel = Math.floor(kernelSize / 2);
    for (let i = 0; i < signal.length; i++) {
      let sum = 0;
      for (let j = 0; j < kernelSize; j++) {
        const idx = i + j - halfKernel;
        if (idx >= 0 && idx < signal.length) {
          sum += signal[idx] * kernel[j];
        }
      }
      result.push(sum);
    }
    return result;
  }
};

export const FFTUtils = {
  computeFFT(signal) {
    const n = signal.length;
    const paddedLength = Math.pow(2, Math.ceil(Math.log2(n)));
    const paddedSignal = [...signal, ...Array(paddedLength - n).fill(0)];
    const fft = this.fftRecursive(paddedSignal);
    const magnitude = [];
    for (let i = 0; i < fft.length / 2; i++) {
      const { real, imag } = fft[i];
      magnitude.push(Math.sqrt(real * real + imag * imag) / paddedLength);
    }
    const frequency = [];
    for (let i = 0; i < magnitude.length; i++) {
      frequency.push(i / paddedLength);
    }
    return { magnitude, frequency };
  },

  fftRecursive(signal) {
    const n = signal.length;
    if (n === 1) return [{ real: signal[0], imag: 0 }];
    const even = [], odd = [];
    for (let i = 0; i < n; i++) {
      if (i % 2 === 0) even.push(signal[i]);
      else odd.push(signal[i]);
    }
    const evenFFT = this.fftRecursive(even);
    const oddFFT = this.fftRecursive(odd);
    const result = Array(n);
    for (let k = 0; k < n / 2; k++) {
      const angle = (-2 * Math.PI * k) / n;
      const wr = Math.cos(angle), wi = Math.sin(angle);
      const { real: oddReal, imag: oddImag } = oddFFT[k];
      const tReal = wr * oddReal - wi * oddImag;
      const tImag = wr * oddImag + wi * oddReal;
      result[k] = { real: evenFFT[k].real + tReal, imag: evenFFT[k].imag + tImag };
      result[k + n / 2] = { real: evenFFT[k].real - tReal, imag: evenFFT[k].imag - tImag };
    }
    return result;
  },

  magnitudeToDb(magnitude) {
    const minDb = -80;
    return magnitude.map(m => {
      const db = 20 * Math.log10(Math.max(m, 1e-10));
      return Math.max(db, minDb);
    });
  }
};
