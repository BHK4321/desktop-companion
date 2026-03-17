import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import 'platform/sse_client.dart';

const _streamEndpoint = 'http://127.0.0.1:8000/api/chat/stream';

void main() {
  runApp(const DesktopCompanion());
}

class DesktopCompanion extends StatelessWidget {
  const DesktopCompanion({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Desktop Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: const ChatHome(),
    );
  }
}

class ChatHome extends StatefulWidget {
  const ChatHome({super.key});

  @override
  State<ChatHome> createState() => _ChatHomeState();
}

class _ChatHomeState extends State<ChatHome> with SingleTickerProviderStateMixin {
  final List<ChatMessage> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late final AnimationController _blackHoleController;
  bool _isChatOpen = false;
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    _blackHoleController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 16),
    )..repeat();
  }

  @override
  void dispose() {
    _blackHoleController.dispose();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _handleSend() async {
    final trimmed = _controller.text.trim();
    if (trimmed.isEmpty || _isSending) return;
    setState(() {
      _messages.add(ChatMessage(role: 'user', content: trimmed));
      _isChatOpen = true;
      _isSending = true;
      _controller.clear();
    });
    _scheduleScroll();

    final history = _messages
        .map((message) => {'role': message.role, 'content': message.content})
        .toList();
    setState(() => _messages.add(const ChatMessage(role: 'assistant', content: '')));
    await _streamAgentResponse(history);
  }

  Future<void> _streamAgentResponse(List<Map<String, String>> history) async {
    debugPrint('Starting streaming request with history length ${history.length}');
    try {
      await subscribeToSse(_streamEndpoint, history, _handleStreamingChunk);
      debugPrint('Streaming request completed');
    } catch (error) {
      debugPrint('Streaming error: $error');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Streaming error: $error'),
          backgroundColor: Colors.deepOrangeAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  void _handleStreamingChunk(String content) {
    debugPrint('Received streaming chunk (${content.length} chars)');
    if (!mounted) return;
    setState(() {
      final index = _messages.lastIndexWhere((msg) => msg.role == 'assistant');
      if (index != -1) {
        final updated = _messages[index].content + content;
        _messages[index] = ChatMessage(role: 'assistant', content: updated);
      }
    });
    _scheduleScroll();
  }

  void _scheduleScroll() {
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
  }

  void _scrollToBottom() {
    if (!_scrollController.hasClients) return;
    _scrollController.animateTo(
      _scrollController.position.maxScrollExtent + 60,
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF02030A), Color(0xFF090C1D), Color(0xFF0F1636)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Row(
            children: [
              AnimatedContainer(
                width: _isChatOpen ? 360 : 0,
                duration: const Duration(milliseconds: 500),
                curve: Curves.easeInOut,
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.7),
                  border: Border(
                    right: BorderSide(color: Colors.white24, width: _isChatOpen ? 1 : 0),
                  ),
                ),
                child: _isChatOpen ? _buildChatPanel() : const SizedBox.shrink(),
              ),
              Expanded(
                child: Stack(
                  children: [
                    Positioned.fill(child: _EnergyOrb(animation: _blackHoleController)),
                    if (!_isChatOpen) _buildChatTrigger(),
                    Positioned(
                      left: 32,
                      bottom: 32,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            'The companion awakens',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 18,
                              letterSpacing: 1.1,
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Whisper your query to release the spin.',
                            style: TextStyle(
                              color: Colors.white38,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChatPanel() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
      child: Column(
        children: [
          const Text(
            'Chat',
            style: TextStyle(fontSize: 22, letterSpacing: 1.4, fontWeight: FontWeight.w600),
          ),
          if (_isSending)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 6),
              child: LinearProgressIndicator(
                minHeight: 3,
                backgroundColor: Colors.white12,
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF2EE5FF)),
              ),
            ),
          const Divider(color: Colors.white24),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: _messages.length,
              padding: const EdgeInsets.only(bottom: 16),
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
          const SizedBox(height: 8),
          _buildComposer(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.role == 'user';
    final content = message.content.isEmpty ? (_isSending ? '• • •' : '') : message.content;
    final radius = isUser
        ? const BorderRadius.only(
            topLeft: Radius.circular(18),
            topRight: Radius.circular(6),
            bottomLeft: Radius.circular(18),
            bottomRight: Radius.circular(18),
          )
        : const BorderRadius.only(
            topLeft: Radius.circular(6),
            topRight: Radius.circular(18),
            bottomLeft: Radius.circular(18),
            bottomRight: Radius.circular(18),
          );
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 260),
            child: Container(
              decoration: BoxDecoration(
                color: isUser ? Colors.deepPurpleAccent : Colors.white,
                borderRadius: radius,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black45,
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
              child: MarkdownBody(
                data: content.isEmpty ? '• • •' : content,
                styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
                  p: TextStyle(color: isUser ? Colors.white : Colors.black87),
                  listBullet: TextStyle(color: isUser ? Colors.white : Colors.black87),
                  h1: TextStyle(color: isUser ? Colors.white : Colors.black87, fontSize: 20),
                ),
                selectable: false,
                softLineBreak: true,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComposer() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            enabled: !_isSending,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Type your message...',
              hintStyle: TextStyle(color: Colors.white54),
              filled: true,
              fillColor: Colors.white10,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            ),
            textInputAction: TextInputAction.send,
            onSubmitted: (_) => _handleSend(),
          ),
        ),
        const SizedBox(width: 12),
        GestureDetector(
          onTap: _handleSend,
          child: Container(
            height: 48,
            width: 48,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFF6F6BFF), Color(0xFF2EE5FF)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.blueAccent.withOpacity(0.5),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Icon(
              _isSending ? Icons.send_and_archive : Icons.send,
              color: Colors.white,
            ),
          ),
        )
      ],
    );
  }

  Widget _buildChatTrigger() {
    return Positioned(
      right: 48,
      bottom: 52,
      child: GestureDetector(
        onTap: () {
          setState(() => _isChatOpen = true);
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 18),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.7),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: Colors.white24),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.bubble_chart, color: Colors.white70, size: 20),
              SizedBox(width: 10),
              Text(
                'Start chat',
                style: TextStyle(color: Colors.white70, letterSpacing: 1.1),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ChatMessage {
  final String role;
  final String content;
  const ChatMessage({required this.role, required this.content});
}

class _EnergyOrb extends StatelessWidget {
  const _EnergyOrb({required this.animation});

  final Animation<double> animation;

  @override
  Widget build(BuildContext context) {
    const baseSize = 340.0;
    const outerGlowRadius = baseSize + 160;
    return Center(
      child: AnimatedBuilder(
        animation: animation,
        builder: (context, child) {
          final pulse = (math.sin(animation.value * 2 * math.pi) + 1) / 2;
          final angle = animation.value * 2 * math.pi;
          final flameTheta = angle * 1.8;
          final flameOffset = Offset(math.cos(flameTheta) * 48, math.sin(flameTheta) * 10);
          return Stack(
            alignment: Alignment.center,
            children: [
              Transform.rotate(
                angle: angle * 0.25,
                child: Container(
                  width: outerGlowRadius,
                  height: outerGlowRadius,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        Color(0xFF0C1F48).withOpacity(0.7 + pulse * 0.2),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 1.0],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Color(0xFF1D4DE2).withOpacity(0.35 + pulse * 0.2),
                        blurRadius: 120 + pulse * 40,
                        spreadRadius: 28,
                      ),
                    ],
                  ),
                ),
              ),
              Transform.rotate(
                angle: angle * 0.7,
                child: Container(
                  width: baseSize + 80,
                  height: baseSize + 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const SweepGradient(
                      colors: [
                        Colors.transparent,
                        Color(0xFF1D3F75),
                        Color(0xFF0A1F3F),
                        Colors.transparent,
                      ],
                      stops: [0.0, 0.25, 0.6, 1.0],
                      tileMode: TileMode.clamp,
                    ),
                  ),
                ),
              ),
              Transform.rotate(
                angle: angle * 0.35,
                child: Container(
                  width: baseSize + 40,
                  height: baseSize + 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Color(0xFF0E255C).withOpacity(0.4 + pulse * 0.25),
                        blurRadius: 60 + pulse * 25,
                        spreadRadius: 18,
                      ),
                    ],
                    gradient: RadialGradient(
                      colors: [
                        Colors.transparent,
                        Color(0xFF0D1F46).withOpacity(0.75),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.5, 1.0],
                    ),
                  ),
                ),
              ),
              Transform.rotate(
                angle: angle * 0.9,
                child: Container(
                  width: baseSize,
                  height: baseSize,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const RadialGradient(
                      colors: [
                        Color(0xFF0A1B3A),
                        Color(0xFF0F2247),
                        Color(0xFF020316),
                      ],
                      stops: [0.0, 0.45, 1.0],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Color(0xFF2EE5FF).withOpacity(0.4 + pulse * 0.15),
                        blurRadius: 25 + pulse * 20,
                        spreadRadius: 12,
                      ),
                    ],
                  ),
                ),
              ),
              Transform.rotate(
                angle: angle,
                child: Container(
                  width: baseSize,
                  height: baseSize,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: SweepGradient(
                      colors: [
                        Colors.transparent,
                        Color(0xFF2AA6FF).withOpacity(0.35 + pulse * 0.25),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.45, 1.0],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
