import 'dart:async';
import 'api_service.dart';
import 'dart:html' as html;

class TTSService {
  html.AudioElement? _currentAudio;

  /// Redă textul folosind API-ul backend pentru TTS
  Future<void> speak(String text) async {
    try {
      if (text.isEmpty) {
        print('Text gol, nu se poate reda');
        return;
      }

      // Oprește redarea curentă dacă există
      await stop();

      // Generează audio folosind backend-ul
      final audioUrl = await ApiService.textToSpeech(text);
      
      // Redă audio-ul folosind HTML5 Audio (funcționează în web)
      await _playAudio(audioUrl);
      
    } catch (e) {
      print('Eroare la redarea vorbirii: $e');
      rethrow;
    }
  }

  /// Redă audio-ul folosind HTML5 Audio API
  Future<void> _playAudio(String audioUrl) async {
    try {
      // Creează un element audio nou
      _currentAudio = html.AudioElement()
        ..src = audioUrl
        ..autoplay = true;
      
      // Așteaptă ca audio-ul să se încarce și să pornească
      await _currentAudio!.onLoadedData.first;
      
      // Redă audio-ul
      await _currentAudio!.play();
      
      print('Redare audio: $audioUrl');
    } catch (e) {
      print('Eroare la redarea audio: $e');
      throw Exception('Nu s-a putut reda audio: $e');
    }
  }

  Future<void> stop() async {
    if (_currentAudio != null) {
      _currentAudio!.pause();
      _currentAudio!.src = '';
      _currentAudio = null;
    }
  }

  Future<void> pause() async {
    if (_currentAudio != null) {
      _currentAudio!.pause();
    }
  }

  /// Redă o secvență de texte concatenate
  Future<void> speakSequence(List<String> texts) async {
    if (texts.isEmpty) return;
    final combinedText = texts.join(' ');
    await speak(combinedText);
  }
}


