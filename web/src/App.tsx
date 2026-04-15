import { useState, useEffect } from 'react';
import { FileText, Calculator, Clock, User, RefreshCw } from 'lucide-react';

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

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/records');
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

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <header className="mb-10 text-center relative max-w-7xl mx-auto">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
          <span className="text-blue-600">SmartHub</span> Dashboard
        </h1>
        <p className="mt-2 text-gray-500">Система аналізу та збереження студентських конспектів</p>
        
        {/* Кнопка оновлення даних */}
        <button 
          onClick={fetchRecords}
          className="absolute right-0 top-2 flex items-center bg-white border border-gray-200 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50 hover:text-blue-600 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Оновити
        </button>
      </header>

      <main className="max-w-7xl mx-auto">
        {loading ? (
          <div className="text-center text-gray-500 py-10">Завантаження конспектів з бази даних...</div>
        ) : records.length === 0 ? (
          <div className="text-center text-gray-500 py-10">База даних порожня. Відправте фото боту!</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {records.map((record) => (
              <div key={record.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                
                {/* Шапка картки */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-2">
                    {record.docType === 'math_exam' ? (
                      <Calculator className="w-5 h-5 text-purple-500" />
                    ) : (
                      <FileText className="w-5 h-5 text-blue-500" />
                    )}
                    <span className="font-semibold text-gray-700 capitalize">
                      {record.docType.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded-full flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {record.date}
                  </span>
                </div>

                {/* Блок з текстом */}
                <div className="bg-gray-50 rounded-xl p-4 mb-4 h-40 overflow-y-auto">
                  <pre className="text-sm text-gray-600 font-mono whitespace-pre-wrap">
                    {record.content}
                  </pre>
                </div>

                {/* Підвал картки */}
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center">
                    <User className="w-4 h-4 mr-2" />
                    <span>Автор: <span className="font-medium text-gray-900">{record.author}</span></span>
                  </div>
                </div>
                
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;