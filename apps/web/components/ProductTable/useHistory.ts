import { useState, useCallback } from 'react';
import { HistoryAction, Product } from './types';

const MAX_HISTORY = 10;

export function useHistory() {
  const [history, setHistory] = useState<HistoryAction[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);

  const addAction = useCallback((action: HistoryAction) => {
    setHistory((prev) => {
      const newHistory = prev.slice(0, currentIndex + 1);
      newHistory.push(action);
      if (newHistory.length > MAX_HISTORY) {
        newHistory.shift();
        return newHistory;
      }
      return newHistory;
    });
    setCurrentIndex((prev) => Math.min(prev + 1, MAX_HISTORY - 1));
  }, [currentIndex]);

  const undo = useCallback((): HistoryAction | null => {
    if (currentIndex < 0) return null;
    const action = history[currentIndex];
    setCurrentIndex((prev) => prev - 1);
    return action;
  }, [currentIndex, history]);

  const redo = useCallback((): HistoryAction | null => {
    if (currentIndex >= history.length - 1) return null;
    const action = history[currentIndex + 1];
    setCurrentIndex((prev) => prev + 1);
    return action;
  }, [currentIndex, history]);

  const canUndo = currentIndex >= 0;
  const canRedo = currentIndex < history.length - 1;

  return { addAction, undo, redo, canUndo, canRedo };
}
