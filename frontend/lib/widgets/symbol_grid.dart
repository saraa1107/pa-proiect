import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/symbol.dart';

class SymbolGrid extends StatelessWidget {
  final List<Symbol> symbols;
  final Function(Symbol) onSymbolTap;
  final Function(Symbol)? onSymbolDoubleTap;
  final Function(Symbol)? onSymbolLongPress;
  final Set<int>? favoriteIds;
  final Function(Symbol)? onToggleFavorite;

  const SymbolGrid({
    super.key,
    required this.symbols,
    required this.onSymbolTap,
    this.onSymbolDoubleTap,
    this.onSymbolLongPress,
    this.favoriteIds,
    this.onToggleFavorite,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(16.0),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: symbols.length,
      itemBuilder: (context, index) {
        final symbol = symbols[index];
        final isFavorite = favoriteIds?.contains(symbol.id) ?? false;
        return _SymbolCard(
          symbol: symbol,
          isFavorite: isFavorite,
          onTap: () => onSymbolTap(symbol),
          onDoubleTap: onSymbolDoubleTap != null ? () => onSymbolDoubleTap!(symbol) : null,
          onLongPress: onSymbolLongPress != null ? () => onSymbolLongPress!(symbol) : null,
          onToggleFavorite: onToggleFavorite != null ? () => onToggleFavorite!(symbol) : null,
        );
      },
    );
  }
}

class _SymbolCard extends StatelessWidget {
  final Symbol symbol;
  final bool isFavorite;
  final VoidCallback onTap;
  final VoidCallback? onDoubleTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onToggleFavorite;

  const _SymbolCard({
    required this.symbol,
    required this.isFavorite,
    required this.onTap,
    this.onDoubleTap,
    this.onLongPress,
    this.onToggleFavorite,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      child: Stack(
        children: [
          InkWell(
            onTap: onTap,
            onDoubleTap: onDoubleTap,
            onLongPress: onLongPress,
            borderRadius: BorderRadius.circular(12),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Expanded(
                  flex: 3,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: CachedNetworkImage(
                      imageUrl: symbol.imageUrl,
                      placeholder: (context, url) => const Center(
                        child: CircularProgressIndicator(),
                      ),
                      errorWidget: (context, url, error) => const Icon(
                        Icons.image_not_supported,
                        size: 40,
                      ),
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                Expanded(
                  flex: 1,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0),
                    child: Text(
                      symbol.name,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Buton favorite în colțul dreapta-sus
          if (onToggleFavorite != null)
            Positioned(
              top: 4,
              right: 4,
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: onToggleFavorite,
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.9),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isFavorite ? Icons.star : Icons.star_border,
                      color: isFavorite ? Colors.amber : Colors.grey,
                      size: 20,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}


