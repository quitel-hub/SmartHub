import { useState, useEffect, useMemo, startTransition } from 'react';
import { 
  FileText, 
  Calculator, 
  Clock, 
  User, 
  RefreshCw, 
  Search, 
  Sparkles, 
  Zap, 
  CheckCircle2, 
  Edit3, 
  Check, 
  BookOpen,
  Globe
} from 'lucide-react';
import { translations } from './i18n';
import type { Language } from './i18n';

interface OCRRecord {
  id: string;
  author: string;
  docType: string;
  date: string;
  content: string;
}

function App() {
  const [records, setRecords] = useState<OCRRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  const [lang, setLang] = useState<Language>('ukr');
  const t = translations[lang] || translations.ukr;

  const [translatedContent, setTranslatedContent] = useState<Record<string, string>>({});
  const [cardTab, setCardTab] = useState<Record<string, 'orig' | 'trans'>>({});
  const [isTranslating, setIsTranslating] = useState<Record<string, boolean>>({});

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/records');
      if (!response.ok) throw new Error('Network error');
      const data = await response.json();
      setRecords(data);
    } catch (error) {
      console.error("Failed to fetch records:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const categories = useMemo(() => {
    const types = new Set(records.map(r => r.docType));
    return ['all', ...Array.from(types)];
  }, [records]);

  const filteredRecords = useMemo(() => {
    return records.filter(record => {
      const safeContent = record.content || '';
      const safeAuthor = record.author || '';
      const matchesSearch = safeContent.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            safeAuthor.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || record.docType === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [records, searchQuery, selectedCategory]);

  const saveEdit = (id: string) => {
    setRecords((prev: OCRRecord[]) => 
      prev.map(rec => rec.id === id ? { ...rec, content: editValue } : rec)
    );
    setEditingId(null);
    setTranslatedContent(prev => ({ ...prev, [id]: '' }));
  };

  const startEdit = (record: OCRRecord) => {
    setEditingId(record.id);
    setEditValue(record.content || '');
    setCardTab(prev => ({ ...prev, [record.id]: 'orig' }));
  };

  const toggleLanguage = () => {
    startTransition(() => {
      setLang((prev: Language) => prev === 'ukr' ? 'eng' : 'ukr');
    });
  };

  const handleTabChange = async (id: string, text: string, targetTab: 'orig' | 'trans') => {
    setCardTab(prev => ({ ...prev, [id]: targetTab }));
    
    if (targetTab === 'trans' && !translatedContent[id]) {
      setIsTranslating(prev => ({ ...prev, [id]: true }));
      try {
        const targetLangCode = lang === 'ukr' ? 'en' : 'uk';
        const res = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text || '', target: targetLangCode })
        });
        if (!res.ok) throw new Error('API Translation failed');
        const data = await res.json();
        setTranslatedContent(prev => ({ ...prev, [id]: data.translated }));
      } catch (err) {
        console.error(err);
        setTranslatedContent(prev => ({ ...prev, [id]: '⚠️ Помилка перекладу / Translation error' }));
      } finally {
        setIsTranslating(prev => ({ ...prev, [id]: false }));
      }
    }
  };

  const origFlag = lang === 'ukr' ? '🇺🇦' : '🇬🇧';
  const transFlag = lang === 'ukr' ? '🇬🇧' : '🇺🇦';

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500 selection:text-white">
      <div className="h-1.5 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 font-semibold text-xs tracking-wider uppercase border border-blue-500/20">
                {t.header.version}
              </span>
              <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" /> {t.header.live}
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mt-2 text-white">
              <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">{t.header.title}</span>{t.header.subtitle}
            </h1>
            <p className="text-sm text-slate-400 mt-1">{t.header.desc}</p>
          </div>
          
          <div className="self-start md:self-auto flex items-center gap-3">
            <button 
              onClick={toggleLanguage}
              className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-3 py-2.5 rounded-xl transition-all text-xs font-semibold uppercase tracking-wider cursor-pointer"
            >
              <Globe className="w-4 h-4 text-indigo-400" />
              <span>{lang}</span>
            </button>

            <button 
              onClick={fetchRecords}
              disabled={loading}
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-4 py-2.5 rounded-xl transition-all active:scale-95 shadow-sm text-sm font-medium cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 text-blue-400 ${loading ? 'animate-spin' : ''}`} />
              <span>{t.header.sync}</span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-800/50 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between backdrop-blur-sm">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{t.metrics.dbTitle}</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-4xl font-extrabold text-white">{records.length}</span>
              <span className="text-xs text-blue-400 font-medium">{t.metrics.dbCount}</span>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-1.5 text-xs text-slate-400">
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <span>{t.metrics.dbFootnote}</span>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between backdrop-blur-sm">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{t.metrics.speedTitle}</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-4xl font-extrabold text-emerald-400">4.2x</span>
              <span className="text-xs text-slate-400 font-medium">{t.metrics.speedCount}</span>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-1.5 text-xs text-slate-400">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>{t.metrics.speedFootnote}</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-900/40 to-indigo-900/40 border border-blue-500/20 rounded-2xl p-5 flex flex-col justify-between">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-blue-400 fill-blue-400" /> {t.metrics.benchTitle}
              </span>
              <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded font-mono">{t.metrics.benchBadge}</span>
            </div>
            <div className="space-y-2.5 mt-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">{t.metrics.seq}</span>
                  <span className="font-mono text-rose-400 font-medium">9.51s</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-rose-500/80 rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-blue-300 font-medium">{t.metrics.par}</span>
                  <span className="font-mono text-emerald-400 font-bold">2.26s</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: '24%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-4 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder={t.search.placeholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="flex flex-wrap gap-1.5 w-full md:w-auto justify-start">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize cursor-pointer ${
                  selectedCategory === cat 
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat === 'all' ? t.search.all : cat.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 border border-slate-800 rounded-2xl bg-slate-800/10">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mb-3" />
            <p className="text-slate-400 text-sm">{t.states.loading}</p>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="text-center py-20 border border-slate-800 rounded-2xl bg-slate-800/10">
            <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3 stroke-1" />
            <p className="text-slate-300 font-medium">{t.states.notFound}</p>
            <p className="text-slate-500 text-xs mt-1">{t.states.notFoundSub}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRecords.map((record) => {
              const isEditing = editingId === record.id;
              const currentTab = cardTab[record.id] || 'orig';
              const activeSpinner = isTranslating[record.id];
              
              const displayContent = currentTab === 'orig' 
                ? (record.content || t.cards.emptyContent)
                : (translatedContent[record.id] || '');

              return (
                <div 
                  key={record.id} 
                  className="bg-slate-800/40 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all group backdrop-blur-sm"
                >
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 group-hover:border-slate-700 transition-colors">
                          {record.docType === 'math_exam' ? (
                            <Calculator className="w-4 h-4 text-purple-400" />
                          ) : (
                            <FileText className="w-4 h-4 text-blue-400" />
                          )}
                        </div>
                        <div>
                          <span className="block text-xs font-semibold text-slate-300 capitalize">
                            {record.docType.replace('_', ' ')}
                          </span>
                          <span className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                            <Clock className="w-2.5 h-2.5" /> {record.date || t.cards.recent}
                          </span>
                        </div>
                      </div>

                      {!isEditing ? (
                        <button 
                          onClick={() => startEdit(record)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-slate-700/50 rounded-md text-slate-400 hover:text-slate-200 cursor-pointer"
                          title="Редагувати запис"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button 
                          onClick={() => saveEdit(record.id)}
                          className="flex items-center gap-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded-md text-xs font-medium hover:bg-emerald-500/30 cursor-pointer"
                        >
                          <Check className="w-3 h-3" /> {t.cards.save}
                        </button>
                      )}
                    </div>
                    {!isEditing && (
                      <div className="flex bg-slate-900/60 p-1 rounded-lg border border-slate-800/80 mb-2">
                        <button
                          onClick={() => handleTabChange(record.id, record.content, 'orig')}
                          className={`flex-1 py-1 text-[10px] font-semibold rounded-md transition-all flex items-center justify-center gap-1 cursor-pointer ${
                            currentTab === 'orig' ? 'bg-slate-800 text-blue-400 shadow-sm' : 'text-slate-500 hover:text-slate-400'
                          }`}
                        >
                          <span>{origFlag}</span> {t.cards.tabOrig}
                        </button>
                        <button
                          onClick={() => handleTabChange(record.id, record.content, 'trans')}
                          className={`flex-1 py-1 text-[10px] font-semibold rounded-md transition-all flex items-center justify-center gap-1 cursor-pointer ${
                            currentTab === 'trans' ? 'bg-slate-800 text-emerald-400 shadow-sm' : 'text-slate-500 hover:text-slate-400'
                          }`}
                        >
                          {activeSpinner ? (
                            <RefreshCw className="w-3 h-3 animate-spin text-emerald-500" />
                          ) : (
                            <span>{transFlag}</span>
                          )} {t.cards.tabTrans}
                        </button>
                      </div>
                    )}
                    <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 mb-4 h-40 overflow-y-auto custom-scrollbar">
                      {isEditing ? (
                        <textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="w-full h-full bg-transparent text-xs text-slate-200 font-mono resize-none focus:outline-none"
                        />
                      ) : (
                        <pre className={`text-xs font-mono whitespace-pre-wrap leading-relaxed ${currentTab === 'trans' ? 'text-emerald-100/90 font-sans' : 'text-slate-300'}`}>
                          {displayContent}
                        </pre>
                      )}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
                    <div className="flex items-center gap-1.5 truncate max-w-[180px]">
                      <User className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
                      <span className="truncate">{t.cards.student} <span className="font-medium text-slate-400">{record.author || t.cards.anon}</span></span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-600 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      ID: #{record.id}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
      `}</style>
    </div>
  );
}

export default App;