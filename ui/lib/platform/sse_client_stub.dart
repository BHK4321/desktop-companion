import 'dart:async';

import 'sse_client_types.dart';

Future<void> subscribeToSse(
    String endpoint,
    List<Map<String, String>> history,
    SseChunkHandler onChunk,
    ) {
  return Future.error(UnsupportedError('SSE client is not supported on this platform.'));
}
