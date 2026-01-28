import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/sentence_provider.dart';
import '../models/symbol.dart';

class SentenceBar extends StatelessWidget {
  final VoidCallback? onSpeak;
  final VoidCallback? onClear;
  final List<Symbol>? symbols;
  final bool? isPlaying;

  const SentenceBar({
    super.key,
    this.onSpeak,
    this.onClear,
    this.symbols,
    this.isPlaying,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<SentenceProvider>(
      builder: (context, provider, _) {
        final displaySymbols = symbols ?? provider.sentence;
        return Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            border: Border(
              bottom: BorderSide(color: Colors.blue.shade200),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Bara cu simboluri
              Container(
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: displaySymbols.isEmpty
                    ? const Center(
                        child: Text(
                          'Apasă pe simboluri pentru a construi o propoziție',
                          style: TextStyle(color: Colors.grey),
                        ),
                      )
                    : ListView.builder(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.all(8),
                        itemCount: displaySymbols.length,
                        itemBuilder: (context, index) {
                          final symbol = displaySymbols[index];
                          return Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: GestureDetector(
                              onTap: () => provider.removeSymbolAt(index),
                              child: Container(
                                width: 64,
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade100,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Expanded(
                                      child: ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: Image.network(
                                          symbol.imageUrl,
                                          fit: BoxFit.cover,
                                          errorBuilder: (_, __, ___) =>
                                              const Icon(Icons.image_not_supported),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      symbol.name,
                                      style: const TextStyle(fontSize: 10),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      textAlign: TextAlign.center,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        },
                      ),
              ),
              const SizedBox(height: 8),
              // Butoane
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: displaySymbols.isEmpty ? null : onSpeak,
                      icon: const Icon(Icons.volume_up),
                      label: const Text('Pronunță'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: displaySymbols.isEmpty ? null : onClear,
                      icon: const Icon(Icons.clear),
                      label: const Text('Șterge'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
