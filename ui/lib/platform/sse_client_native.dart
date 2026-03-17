import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'sse_client_types.dart';

Future<void> subscribeToSse(
  String endpoint,
  List<Map<String, String>> history,
  SseChunkHandler onChunk,
) async {
  final client = HttpClient();
  try {
    final request = await client.postUrl(Uri.parse(endpoint));
    request.headers.contentType = ContentType.json;
    request.add(utf8.encode(jsonEncode({'messages': history})));

    final response = await request.close();
    await for (final line
        in response.transform(utf8.decoder).transform(const LineSplitter())) {
      if (!line.startsWith('data:')) continue;
      final payload = line.substring(5).trim();
      if (payload.isEmpty) continue;
      if (payload == '[DONE]') break;
      try {
        final chunk = jsonDecode(payload) as Map<String, dynamic>;
        final possibleContent = chunk['content'] as String?;
        final nestedPayload = chunk['payload'] as Map<String, dynamic>?;
        final content = possibleContent?.isNotEmpty == true
            ? possibleContent
            : nestedPayload?['content'] as String?;
        if (content == null || content.isEmpty) continue;
        onChunk(content);
      } catch (_) {
        // ignore malformed payloads
      }
    }
  } finally {
    client.close(force: true);
  }
}
