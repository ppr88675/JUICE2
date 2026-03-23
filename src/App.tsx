/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Search, Coffee, Flame, Loader2, Info, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { DrinkResponse } from './types';
import { getDrinkRecommendations } from './services/gemini';

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DrinkResponse | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const result = await getDrinkRecommendations(searchTerm);
      if (result) {
        setData(result);
        setActiveTab(0);
      } else {
        setError('找不到該店家的資訊，請換個名字試試。');
      }
    } catch (err) {
      setError('獲取推薦失敗，請檢查 API 設定。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const CalorieIcon = ({ level }: { level: string }) => {
    const color = level === 'Low' ? 'text-green-500' : level === 'Medium' ? 'text-yellow-500' : 'text-red-500';
    return <span className={`${color} font-bold`}>{level === 'Low' ? '🟢' : level === 'Medium' ? '🟡' : '🔴'} {level}</span>;
  };

  return (
    <div className="min-h-screen bg-tea-beige font-sans pb-20">
      {/* Header */}
      <header className="bg-white shadow-sm py-6 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-tea-dark flex items-center justify-center gap-2">
            🧋 台灣手搖飲達人
          </h1>
          <p className="text-tea-accent mt-2">不知道喝什麼？輸入店名，我幫你挑 10 個！</p>
          
          <form onSubmit={handleSearch} className="mt-6 flex gap-2 max-w-md mx-auto">
            <input
              type="text"
              placeholder="請輸入飲料店名稱（例如：五十嵐、一沐日）"
              className="flex-grow px-4 py-3 rounded-xl border border-tea-accent/30 focus:outline-none focus:ring-2 focus:ring-tea-green bg-white shadow-inner"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-tea-dark text-white px-6 py-3 rounded-xl font-bold hover:bg-tea-dark/90 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
              搜尋
            </button>
          </form>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 mt-8">
        {loading && (
          <div className="text-center py-20">
            <Loader2 className="animate-spin text-tea-dark mx-auto mb-4" size={48} />
            <p className="text-tea-dark font-medium animate-pulse">正在從 {searchTerm} 的菜單中尋找最強飲品...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-200 text-center">
            {error}
          </div>
        )}

        {data && !loading && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            {/* Shop Info */}
            <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl mb-8 flex items-start gap-3">
              <Info className="text-blue-500 mt-1 shrink-0" size={20} />
              <div>
                <h2 className="font-bold text-blue-900">✨ {data.shop_info.name}</h2>
                <p className="text-blue-700 text-sm">{data.shop_info.slogan}</p>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-4 no-scrollbar">
              {data.recommendations.map((cat, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveTab(idx)}
                  className={`px-6 py-2 rounded-full whitespace-nowrap font-bold transition-all ${
                    activeTab === idx
                      ? 'bg-tea-dark text-white shadow-lg'
                      : 'bg-white text-tea-accent border border-tea-accent/20 hover:bg-tea-green/30'
                  }`}
                >
                  {cat.category}
                </button>
              ))}
            </div>

            {/* Items Grid */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {data.recommendations[activeTab].items.map((item, idx) => (
                  <div key={idx} className="bg-white rounded-2xl p-6 shadow-sm border border-tea-accent/10 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-tea-dark">{item.name}</h3>
                      <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded text-gray-600">{item.price_range}</span>
                    </div>
                    <p className="text-gray-600 text-sm mb-6 leading-relaxed">💡 {item.description}</p>
                    
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-50">
                      <div>
                        <p className="text-[10px] text-tea-accent font-bold uppercase mb-1">黃金比例</p>
                        <p className="text-sm font-bold text-tea-dark">{item.best_ratio}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-tea-accent font-bold uppercase mb-1">熱量預估</p>
                        <CalorieIcon level={item.calories} />
                      </div>
                    </div>
                  </div>
                ))}
              </motion.div>
            </AnimatePresence>
          </motion.div>
        )}

        {!data && !loading && (
          <div className="text-center py-20 opacity-30">
            <Sparkles size={64} className="mx-auto mb-4 text-tea-dark" />
            <p>請在上方搜尋框輸入店名開始推薦</p>
          </div>
        )}
      </main>

      <footer className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-t border-tea-accent/10 py-4 text-center text-xs text-tea-accent">
        本資料由 Google Gemini AI 提供，僅供參考，實際菜單以門市為準。
      </footer>
    </div>
  );
}
