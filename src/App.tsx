/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Search, Coffee, Leaf, Zap, Flame, LayoutGrid, List, Loader2, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { DrinkCategory, DrinkRecommendation } from './types';
import { getDrinkRecommendations } from './services/gemini';

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<DrinkRecommendation[]>([]);
  const [activeCategory, setActiveCategory] = useState<DrinkCategory>(DrinkCategory.ALL);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const results = await getDrinkRecommendations(searchTerm);
      setRecommendations(results);
    } catch (err) {
      setError('獲取推薦失敗，請稍後再試。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredData = activeCategory === DrinkCategory.ALL
    ? recommendations
    : recommendations.filter(item => item.category === activeCategory);

  const CalorieIcons = ({ level }: { level: number }) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3].map((i) => (
          <Flame
            key={i}
            size={14}
            className={i <= level ? 'text-orange-500 fill-orange-500' : 'text-gray-300'}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen font-sans">
      {/* Header Section */}
      <header className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-tea-accent/20">
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="bg-tea-green p-2 rounded-full">
              <Coffee className="text-tea-dark" />
            </div>
            <h1 className="text-2xl font-bold text-tea-dark tracking-tight">TeaTime</h1>
          </div>

          <form onSubmit={handleSearch} className="relative w-full md:w-96">
            <input
              type="text"
              placeholder="輸入飲料店名 (例如：50嵐, 迷客夏...)"
              className="w-full pl-10 pr-4 py-2 rounded-full border border-tea-accent/30 focus:outline-none focus:ring-2 focus:ring-tea-green bg-white/50"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search className="absolute left-3 top-2.5 text-tea-accent" size={18} />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-1.5 bg-tea-dark text-white px-4 py-1 rounded-full text-sm hover:bg-tea-dark/90 transition-colors disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : '搜尋'}
            </button>
          </form>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        {!recommendations.length && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <h2 className="text-4xl font-bold text-tea-dark mb-4">今天想喝什麼？</h2>
            <p className="text-tea-accent text-lg">輸入您喜愛的飲料店，讓 AI 為您挑選最棒的組合</p>
          </motion.div>
        )}

        {/* Filters & View Toggle */}
        {(recommendations.length > 0 || loading) && (
          <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
            <div className="flex gap-2 overflow-x-auto pb-2 w-full md:w-auto no-scrollbar">
              {Object.values(DrinkCategory).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-6 py-2 rounded-full whitespace-nowrap transition-all ${
                    activeCategory === cat
                      ? 'bg-tea-dark text-white shadow-md'
                      : 'bg-white text-tea-accent border border-tea-accent/20 hover:bg-tea-green/30'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="flex bg-white rounded-lg p-1 border border-tea-accent/20">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-tea-green text-tea-dark' : 'text-tea-accent'}`}
              >
                <LayoutGrid size={20} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-tea-green text-tea-dark' : 'text-tea-accent'}`}
              >
                <List size={20} />
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 className="animate-spin text-tea-dark" size={48} />
            <p className="text-tea-accent animate-pulse">正在為您調製專屬推薦...</p>
          </div>
        ) : error ? (
          <div className="text-center py-20 text-red-500">{error}</div>
        ) : (
          <AnimatePresence mode="wait">
            {viewMode === 'grid' ? (
              <motion.div
                key="grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {filteredData.map((item) => (
                  <motion.div
                    layout
                    key={item.id}
                    className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-tea-accent/10 flex flex-col"
                  >
                    <div className="h-3 bg-tea-green" />
                    <div className="p-6 flex-grow">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-bold text-tea-accent uppercase tracking-wider">{item.category}</span>
                        <span className="text-xs font-medium bg-tea-beige px-2 py-1 rounded text-tea-dark">{item.priceRange}</span>
                      </div>
                      <h3 className="text-xl font-bold text-tea-dark mb-3">{item.name}</h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-3">{item.reason}</p>
                      
                      <div className="space-y-3 pt-4 border-t border-gray-50">
                        <div className="flex items-center gap-2">
                          <Zap size={14} className="text-yellow-500" />
                          <span className="text-xs font-bold text-tea-dark">黃金比例：</span>
                          <span className="text-xs text-gray-600">{item.goldenRatio}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Flame size={14} className="text-orange-500" />
                          <span className="text-xs font-bold text-tea-dark">熱量分級：</span>
                          <CalorieIcons level={item.calorieLevel} />
                        </div>
                      </div>
                    </div>
                    <button className="w-full py-3 bg-gray-50 text-tea-dark text-sm font-bold flex items-center justify-center gap-1 hover:bg-tea-green transition-colors">
                      查看更多 <ChevronRight size={16} />
                    </button>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {filteredData.map((item) => (
                  <motion.div
                    layout
                    key={item.id}
                    className="bg-white p-4 rounded-xl shadow-sm border border-tea-accent/10 flex flex-col md:flex-row md:items-center justify-between gap-4"
                  >
                    <div className="flex-grow">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="text-lg font-bold text-tea-dark">{item.name}</h3>
                        <span className="text-[10px] bg-tea-green/50 px-2 py-0.5 rounded-full text-tea-dark font-bold">{item.category}</span>
                      </div>
                      <p className="text-sm text-gray-500">{item.reason}</p>
                    </div>
                    <div className="flex items-center gap-6 shrink-0">
                      <div className="text-right">
                        <p className="text-[10px] text-tea-accent font-bold uppercase">黃金比例</p>
                        <p className="text-xs text-tea-dark font-medium">{item.goldenRatio}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] text-tea-accent font-bold uppercase">熱量</p>
                        <CalorieIcons level={item.calorieLevel} />
                      </div>
                      <div className="text-right min-w-[60px]">
                        <p className="text-[10px] text-tea-accent font-bold uppercase">價格</p>
                        <p className="text-xs text-tea-dark font-medium">{item.priceRange}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-4 py-12 text-center text-tea-accent/60 text-sm">
        <p>© 2026 TeaTime - AI 手搖飲推薦專家</p>
        <p className="mt-1">Powered by Google Gemini API</p>
      </footer>
    </div>
  );
}
