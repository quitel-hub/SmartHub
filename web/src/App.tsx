import { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  Calculator, 
  Clock, 
  User, 
  RefreshCw, 
  Search, 
  Edit2, 
  Save, 
  X, 
  BarChart2, 
  Zap, 
  Tag 
} from 'lucide-react';

interface OCRRecord {
  id: string;
  author: string;
  docType: string;
  date: string;
  content: string;
  category?: string;
}

function App() {
  const [records, setRecords] = useState<OCRRecord[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/records');
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

  const handleSaveEdit = async (id: string) => {
    setSaving(true);
    try {
      setRecords(prev => prev.map(rec => rec.id === id ? { ...rec, content: editContent } : rec));
      
      await fetch('/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, content: editContent })
      });
      
      setEditingId(null);
    } catch (error) {
      console.error("Помилка збереження:", error);
      alert("Не вдалося синхронізувати зміни з базою даних.");
    } finally {
      setSaving(false);
    }
  };

  const startEditing = (record: OCRRecord) => {
    setEditingId(record.id);
    setEditContent(record.content);
  };


  const filteredRecords = useMemo(() => {
    return records.filter(record => {
      const matchesSearch = record.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            record.author.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = selectedType === 'all' || record.docType === selectedType;
      return matchesSearch && matchesType;
    });
  }, [records, searchQuery, selectedType]);

  const availableTypes = useMemo(() => {
    const types = new Set(records.map(r => r.docType));
    return Array.from(types);
  }, [records]);

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8 font-sans text-gray-800">
      <header className="mb-8 text-center relative max-w-7xl mx-auto">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
          <span className="text-blue-600">SmartHub</span> Dashboard
        </h1>
        <p className="mt-2 text-gray-500">Система аналізу, редагування та моніторингу конспектів</p>
        
        <button 
          onClick={fetchRecords}
          disabled={loading}
          className="mt-4 md:mt-0 md:absolute right-0 top-2 inline-flex items-center bg-white border border-gray-200 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 hover:text-blue-600 transition-colors shadow-sm text-sm font-medium"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          Оновити базу
        </button>
      </header>

      <main className="max-w-7xl mx-auto">
        
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-8 transition-all hover:border-blue-100">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-6">
            <h2 className="text-lg font-bold text-gray-900 flex items-center">
              <BarChart2 className="w-5 h-5 text-blue-600 mr-2" />
              Аналітика системи та OCR Бенчмарк
            </h2>
            <span className="bg-green-50 text-green-700 text-xs font-bold px-3 py-1 rounded-full flex items-center border border-green-100">
              <Zap className="w-3.5 h-3.5 mr-1 text-green-600 fill-current" />
              Прискорення 4.21x (Багатопотоковість)
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100/80">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Загалом документів</div>
              <div className="text-3xl font-extrabold text-gray-900">{records.length}</div>
              <div className="text-xs text-gray-400 mt-2 flex items-center">
                <Tag className="w-3 h-3 mr-1" /> Категорій виявлено: {availableTypes.length}
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100/80 flex flex-col justify-center">
              <div className="flex justify-between text-xs font-medium text-gray-500 mb-1.5">
                <span>Послідовно (1 потік)</span>
                <span className="text-red-600 font-bold">9.51 сек</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2 overflow-hidden">
                <div className="bg-red-400 h-full rounded-full" style={{ width: '100%' }}></div>
              </div>
              <div className="text-[11px] text-gray-400">Стандартна обробка пакету з 20 фото</div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100/80 flex flex-col justify-center">
              <div className="flex justify-between text-xs font-medium text-gray-500 mb-1.5">
                <span className="text-green-700 font-semibold">Паралельно (Пул з 4 потоків)</span>
                <span className="text-green-600 font-bold">2.26 сек</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2 overflow-hidden">
                <div className="bg-green-500 h-full rounded-full" style={{ width: '24%' }}></div>
              </div>
              <div className="text-[11px] text-gray-400">Оптимізація через ядро ProcessorPool</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Пошук за текстом або автором..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-1 w-full md:w-auto justify-start">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedType === 'all' 
                  ? 'bg-blue-50 text-blue-600 font-semibold' 
                  : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              Усі записи ({records.length})
            </button>
            {availableTypes.map(type => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                  selectedType === type 
                    ? 'bg-blue-50 text-blue-600 font-semibold' 
                    : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                {type.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-center text-gray-400 py-12 font-medium">Завантаження конспектів...</div>
        ) : filteredRecords.length === 0 ? (
          <div className="text-center text-gray-400 py-12 bg-white rounded-2xl border border-dashed border-gray-200">
            За вашим запитом нічого не знайдено.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRecords.map((record) => {
              const isEditing = editingId === record.id;

              return (
                <div 
                  key={record.id} 
                  className={`bg-white rounded-2xl shadow-sm border transition-all flex flex-col justify-between p-6 ${
                    isEditing ? 'border-blue-400 ring-2 ring-blue-50' : 'border-gray-100 hover:shadow-md'
                  }`}
                >
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center space-x-2">
                        {record.docType === 'math_exam' ? (
                          <Calculator className="w-4 h-4 text-purple-500" />
                        ) : (
                          <FileText className="w-4 h-4 text-blue-500" />
                        )}
                        <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                          {record.docType.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-[11px] font-medium bg-gray-50 text-gray-500 px-2 py-0.5 rounded flex items-center border border-gray-100">
                        <Clock className="w-3 h-3 mr-1" />
                        {record.date || 'Невідомо'}
                      </span>
                    </div>

                    {isEditing ? (
                      <div className="mb-4">
                        <textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          rows={6}
                          className="w-full p-3 bg-blue-50/30 border border-blue-200 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-gray-700"
                          placeholder="Введіть розпізнаний текст..."
                        />
                      </div>
                    ) : (
                      <div className="bg-gray-50/80 rounded-xl p-3 mb-4 h-44 overflow-y-auto border border-gray-100/50 scrollbar-thin">
                        <pre className="text-xs text-gray-600 font-mono whitespace-pre-wrap leading-relaxed">
                          {record.content}
                        </pre>
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-gray-50 flex items-center justify-between text-xs text-gray-500 mt-auto">
                    <div className="flex items-center truncate max-w-[140px]">
                      <User className="w-3.5 h-3.5 mr-1.5 text-gray-400 flex-shrink-0" />
                      <span className="truncate">Автор: <span className="font-medium text-gray-900">{record.author}</span></span>
                    </div>

                    <div>
                      {isEditing ? (
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={() => setEditingId(null)}
                            disabled={saving}
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                            title="Скасувати"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleSaveEdit(record.id)}
                            disabled={saving}
                            className="flex items-center space-x-1 bg-blue-600 text-white px-2.5 py-1 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm disabled:opacity-50"
                          >
                            <Save className={`w-3 h-3 ${saving ? 'animate-bounce' : ''}`} />
                            <span>{saving ? '...' : 'Зберегти'}</span>
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => startEditing(record)}
                          className="flex items-center space-x-1 text-gray-400 hover:text-blue-600 px-2 py-1 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          <Edit2 className="w-3 h-3" />
                          <span>Правка</span>
                        </button>
                      )}
                    </div>
                  </div>
                  
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
