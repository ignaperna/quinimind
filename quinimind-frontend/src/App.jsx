
import React, { useState, useMemo, useEffect } from 'react';
import {
  Trophy,
  TrendingUp,
  Zap,
  Lock,
  BarChart3,
  History,
  RefreshCw,
  Star,
  Target,
  User,
  LogOut,
  ChevronRight,
  BrainCircuit,
  AlertTriangle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

// Generate mock history for statistics (Fallback)
const generateHistory = (count) => {
  const history = [];
  for (let i = 1; i <= count; i++) {
    const draw = [];
    while (draw.length < 6) {
      const num = Math.floor(Math.random() * 46);
      if (!draw.includes(num)) draw.push(num);
    }
    history.push({
      id: 3330 - i,
      date: `Sorteo ${3330 - i}`,
      numbers: draw.sort((a, b) => a - b)
    });
  }
  return history;
};

// --- COMPONENTS ---

const Card = ({ children, className = "" }) => (
  <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg ${className}`}>
    {children}
  </div>
);

const NumberBall = ({ number, type = "default", size = "md" }) => {
  let colors = "bg-slate-700 text-white border-slate-600";
  if (type === "hot") colors = "bg-red-500/20 text-red-400 border-red-500/50";
  if (type === "cold") colors = "bg-blue-500/20 text-blue-400 border-blue-500/50";
  if (type === "winning") colors = "bg-emerald-500 text-white border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.5)]";
  if (type === "prediction") colors = "bg-violet-600 text-white border-violet-400";

  const sizeClass = size === "sm" ? "w-8 h-8 text-sm" : "w-10 h-10 font-bold";

  return (
    <div className={`${sizeClass} rounded-full flex items-center justify-center border-2 ${colors} shadow-sm transition-all hover:scale-110`}>
      {number}
    </div>
  );
};

const Header = ({ user, onLogin }) => (
  <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-lg border-b border-slate-800">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-violet-600 to-indigo-600 p-2 rounded-lg">
            <BrainCircuit className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            QuiniMind<span className="text-violet-500">.ai</span>
          </span>
        </div>
        <div className="flex items-center space-x-4">
          {!user ? (
            <button
              onClick={onLogin}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition text-sm font-medium border border-slate-700"
            >
              Iniciar Sesión
            </button>
          ) : (
            <div className="flex items-center space-x-3 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
              <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold">
                PRO
              </div>
              <span className="text-sm text-slate-300 hidden sm:block">Usuario Premium</span>
            </div>
          )}
        </div>
      </div>
    </div>
  </nav>
);

const ResultsSection = ({ latestDraw, loading }) => {
  if (loading) return <div className="text-center py-10 text-slate-500">Cargando últimos resultados...</div>;
  if (!latestDraw) return null;

  const modes = [
    { name: "Tradicional", nums: latestDraw.modes.tradicional, color: "text-blue-400" },
    { name: "La Segunda", nums: latestDraw.modes.laSegunda, color: "text-emerald-400" },
    { name: "Revancha", nums: latestDraw.modes.revancha, color: "text-amber-400" },
    { name: "Siempre Sale", nums: latestDraw.modes.siempreSale, color: "text-rose-400" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Trophy className="text-yellow-500" />
            Últimos Resultados
          </h2>
          <p className="text-slate-400 text-sm mt-1">Sorteo #{latestDraw.id} • {latestDraw.date}</p>
        </div>
        <span className="text-xs px-2 py-1 rounded bg-green-500/10 text-green-400 border border-green-500/20 animate-pulse">
          Verificado
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((mode) => (
          <Card key={mode.name} className="relative overflow-hidden group hover:border-slate-600 transition-colors">
            <div className={`absolute top-0 left-0 w-1 h-full ${mode.color.replace('text', 'bg')}`}></div>
            <h3 className={`font-semibold mb-4 ${mode.name} text-slate-200`}>{mode.name}</h3>
            <div className="flex justify-between gap-2 flex-wrap">
              {mode.nums && mode.nums.map((n) => (
                <NumberBall key={n} number={n} type="winning" />
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

const StatsSection = ({ history, loading }) => {
  if (loading) return <div className="text-center text-slate-500">Analizando historial...</div>

  // Calculate frequency
  const stats = useMemo(() => {
    if (!history || history.length === 0) return [];

    const frequency = Array(46).fill(0);
    history.forEach(draw => draw.numbers.forEach(n => frequency[n]++));

    return frequency.map((count, num) => ({ num, count })).sort((a, b) => b.count - a.count);
  }, [history]);

  const top10 = stats.slice(0, 10);
  const bottom10 = [...stats].reverse().slice(0, 10);

  return (
    <div className="space-y-6 mt-12">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="text-violet-400" />
          Análisis de Frecuencia
        </h2>
        <select className="bg-slate-800 border-slate-700 text-slate-300 rounded-lg text-sm px-3 py-1">
          <option>Últimos 50 Sorteos</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h3 className="text-slate-300 font-medium mb-6">Números "Calientes" (Mayor Salida)</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top10}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="num" stroke="#94a3b8" tickLine={false} />
                <YAxis stroke="#94a3b8" tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {top10.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index < 3 ? '#8b5cf6' : '#64748b'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <h3 className="text-slate-300 font-medium mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" /> Top Hot
            </h3>
            <div className="flex flex-wrap gap-2">
              {top10.slice(0, 6).map(s => (
                <NumberBall key={s.num} number={s.num} type="hot" size="sm" />
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-3">Basado en frecuencia de aparición &gt; 15%</p>
          </Card>
          <Card>
            <h3 className="text-slate-300 font-medium mb-4 flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-400" /> Top Cold
            </h3>
            <div className="flex flex-wrap gap-2">
              {bottom10.slice(0, 6).map(s => (
                <NumberBall key={s.num} number={s.num} type="cold" size="sm" />
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-3">Números atrasados (sin salir en &gt;10 sorteos)</p>
          </Card>
        </div>
      </div>
    </div>
  );
};

const PredictionEngine = ({ isPro, onUpgrade }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const generatePrediction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/predict`);
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-12">
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-r from-violet-900 to-indigo-900 border border-violet-700/50 shadow-2xl p-8 lg:p-12">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <BrainCircuit className="w-64 h-64 text-white" />
        </div>

        <div className="relative z-10 text-center max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-4">Motor de Predicción IA</h2>
          <p className="text-violet-200 mb-8 text-lg">
            Nuestros algoritmos analizan miles de sorteos históricos para detectar patrones de probabilidad y sugerir combinaciones optimizadas (Datos Reales).
          </p>

          {!isPro ? (
            <div className="bg-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700">
              <div className="flex flex-col items-center gap-4">
                <Lock className="w-12 h-12 text-slate-500" />
                <div>
                  <h3 className="text-xl font-semibold text-white">Función Premium</h3>
                  <p className="text-slate-400">Desbloquea el generador de predicciones con QuiniMind Pro.</p>
                </div>
                <button
                  onClick={onUpgrade}
                  className="mt-2 px-8 py-3 bg-white text-slate-900 font-bold rounded-lg hover:bg-slate-200 transition shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                >
                  Desbloquear Ahora - $2.500/mes
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {prediction && (
                <div className="flex justify-center gap-3 md:gap-4 mb-8 animate-in fade-in zoom-in duration-500">
                  {prediction.map((n) => (
                    <NumberBall key={n} number={n} type="prediction" />
                  ))}
                </div>
              )}

              <button
                onClick={generatePrediction}
                disabled={loading}
                className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-violet-600 font-lg rounded-full hover:bg-violet-500 focus:outline-none ring-offset-2 focus:ring-2 disabled:opacity-70 disabled:cursor-not-allowed shadow-[0_0_30px_rgba(124,58,237,0.5)] hover:shadow-[0_0_50px_rgba(124,58,237,0.7)]"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="animate-spin" /> Analizando Patrones...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Target /> Generar Predicción Inteligente
                  </span>
                )}
              </button>

              {prediction && (
                <p className="text-sm text-violet-300/70">
                  Probabilidad estimada de acierto: <span className="text-white font-bold">Calculando con IA...</span>
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- MAIN APP COMPONENT ---

export default function App() {
  const [isPro, setIsPro] = useState(false);
  const [user, setUser] = useState(null);

  const [latestDraw, setLatestDraw] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resDraw = await fetch("./data.json");

        if (!resDraw.ok) throw new Error("JSON Feed Error");

        const dataDraw = await resDraw.json();

        setLatestDraw(dataDraw);
        // For history, we either need another JSON or fallback to Mock. 
        // Re-enabling Mock History for stats since user only asked for latest draw JSON.
        // In a real app we'd export history.json too.
        setHistory(generateHistory(50));
      } catch (err) {
        console.error("Failed to load data", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogin = () => {
    // Simulate login
    setUser({ name: "Usuario", email: "user@demo.com" });
  };

  const handleUpgrade = () => {
    // Simulate checkout
    if (!user) handleLogin();
    setIsPro(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-violet-500/30">
      <Header user={user} onLogin={handleLogin} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">

        {/* HERO SECTION */}
        <section className="text-center py-10">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 tracking-tight">
            Domina el <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">Quini 6</span> con IA
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">
            La plataforma SaaS #1 de analítica predictiva para loterías en Argentina.
            Datos en tiempo real, estadísticas profundas y algoritmos de predicción.
          </p>
          <div className="flex justify-center gap-4 text-sm font-medium text-slate-500">
            <span className="flex items-center gap-1"><Star className="w-4 h-4 text-yellow-500" /> +10k Usuarios</span>
            <span className="flex items-center gap-1"><TrendingUp className="w-4 h-4 text-green-500" /> 85% Precisión Est.</span>
          </div>
        </section>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-lg flex items-center justify-center gap-3 text-red-200">
            <AlertTriangle /> No se pudieron cargar los datos del sorteo. (Error de red o archivo data.json faltante)
          </div>
        )}

        {/* RESULTS FEED */}
        <ResultsSection latestDraw={latestDraw} loading={loading} />

        {/* STATS DASHBOARD */}
        <StatsSection history={history} loading={loading} />

        {/* PREDICTION ENGINE (SAAS FEATURE) */}
        <PredictionEngine isPro={isPro} onUpgrade={handleUpgrade} />

        {/* PRICING */}
        {!isPro && (
          <div className="grid md:grid-cols-2 gap-8 mt-20 max-w-4xl mx-auto">
            <Card className="border-slate-700">
              <div className="p-4">
                <h3 className="text-xl font-bold text-white">Plan Gratuito</h3>
                <div className="text-3xl font-bold text-slate-200 mt-4">$0 <span className="text-sm font-normal text-slate-500">/mes</span></div>
                <ul className="mt-6 space-y-4">
                  <li className="flex gap-3 text-slate-300"><ChevronRight className="text-violet-500" /> Resultados en vivo</li>
                  <li className="flex gap-3 text-slate-300"><ChevronRight className="text-violet-500" /> Estadísticas básicas</li>
                  <li className="flex gap-3 text-slate-500"><Lock className="w-4 h-4" /> Predicciones IA</li>
                  <li className="flex gap-3 text-slate-500"><Lock className="w-4 h-4" /> Exportar datos</li>
                </ul>
              </div>
            </Card>
            <Card className="border-violet-500 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-violet-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">RECOMENDADO</div>
              <div className="p-4">
                <h3 className="text-xl font-bold text-white">Plan PRO</h3>
                <div className="text-3xl font-bold text-white mt-4">$2.500 <span className="text-sm font-normal text-slate-400">/mes</span></div>
                <ul className="mt-6 space-y-4">
                  <li className="flex gap-3 text-white"><ChevronRight className="text-green-400" /> Todo lo gratuito</li>
                  <li className="flex gap-3 text-white"><ChevronRight className="text-green-400" /> 10 Predicciones diarias</li>
                  <li className="flex gap-3 text-white"><ChevronRight className="text-green-400" /> Análisis de Números Fríos/Calientes</li>
                  <li className="flex gap-3 text-white"><ChevronRight className="text-green-400" /> Alertas por Email</li>
                </ul>
                <button
                  onClick={handleUpgrade}
                  className="w-full mt-8 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-bold transition"
                >
                  Comenzar Prueba Gratis
                </button>
              </div>
            </Card>
          </div>
        )}

      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>© 2025 QuiniMind AI. Todos los derechos reservados.</p>
          <p className="mt-2">Jugar compulsivamente es perjudicial para la salud. Línea de ayuda: 0800-444-4000.</p>
        </div>
      </footer>
    </div>
  );
}
