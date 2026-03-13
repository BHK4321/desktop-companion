import 'dart:async';
import 'dart:convert';
import 'dart:html';

import 'sse_client_types.dart';

Future<void> subscribeToSse(
  String endpoint,
  List<Map<String, String>> history,
  SseChunkHandler onChunk,
) {
  final completer = Completer<void>();
  final parser = _SseWebParser(onChunk, completer);
  final xhr = HttpRequest();
  xhr.open('POST', endpoint);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onProgress.listen((_) {
    parser.addChunk(xhr.responseText ?? '');
  });
  xhr.onLoad.listen((_) {
    parser.addChunk(xhr.responseText ?? '', isFinal: true);
    if (!completer.isCompleted) {
      completer.complete();
    }
  });
  xhr.onError.listen((_) {
    if (!completer.isCompleted) {
      completer.completeError(StateError('Failed to open SSE stream.'));
    }
  });
  xhr.send(jsonEncode({'messages': history}));
  return completer.future;
}

class _SseWebParser {
  _SseWebParser(this.onChunk, this.completer);

  final SseChunkHandler onChunk;
  final Completer<void> completer;

  String _buffer = '';
  int _lastLength = 0;
  bool _done = false;

  void addChunk(String text, {bool isFinal = false}) {
    if (_done) return;
    if (text.length < _lastLength) {
      _lastLength = 0;
    }
    if (text.length == _lastLength && !isFinal) return;
    final newData = text.substring(_lastLength);
    _lastLength = text.length;
    _buffer += newData;
    _processBuffer();
    if (isFinal && !_done) {
      _done = true;
      if (!completer.isCompleted) {
        completer.complete();
      }
    }
  }

  void _processBuffer() {
    while (!_done) {
      final eventEnd = _buffer.indexOf('\n\n');
      if (eventEnd == -1) break;
      final block = _buffer.substring(0, eventEnd);
      _buffer = _buffer.substring(eventEnd + 2);
      final lines = block.split(RegExp(r'\r?\n'));
      for (final line in lines) {
        if (!line.startsWith('data:')) continue;
        final payload = line.substring(5).trim();
        if (payload.isEmpty) continue;
        if (payload == '[DONE]') {
          _done = true;
          if (!completer.isCompleted) {
            completer.complete();
          }
          return;
        }
        try {
          final chunk = jsonDecode(payload) as Map<String, dynamic>;
          final content = chunk['content'] as String? ?? '';
          if (content.isEmpty) continue;
          onChunk(content);
        } catch (_) {
          // ignore malformed payloads
        }
      }
    }
  }
}
