// Audio conversion utilities
class AudioConverter {
    static async blobToWav(audioBlob) {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        // Create WAV file
        const numberOfChannels = 1;
        const sampleRate = 16000;
        const bitsPerSample = 16;
        const length = audioBuffer.length * numberOfChannels * (bitsPerSample / 8);
        
        // Create WAV header
        const buffer = new ArrayBuffer(44 + length);
        const view = new DataView(buffer);
        
        // Write WAV header
        AudioConverter.writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + length, true);
        AudioConverter.writeString(view, 8, 'WAVE');
        AudioConverter.writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numberOfChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * numberOfChannels * (bitsPerSample / 8), true);
        view.setUint16(32, numberOfChannels * (bitsPerSample / 8), true);
        view.setUint16(34, bitsPerSample, true);
        AudioConverter.writeString(view, 36, 'data');
        view.setUint32(40, length, true);
        
        // Write audio data
        const data = new Float32Array(audioBuffer.getChannelData(0));
        let offset = 44;
        for (let i = 0; i < data.length; i++) {
            const sample = Math.max(-1, Math.min(1, data[i]));
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
            offset += 2;
        }
        
        return new Blob([buffer], { type: 'audio/wav' });
    }
    
    static writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }
}
