import React, { useState, useEffect } from 'react';
import { 
    fetchTwinState, startReplay, stopReplay, getReplayStatus, fetchExplanation, fetchEngineHistory 
} from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Square, Activity, AlertTriangle, TrendingDown, Info, ShieldAlert } from 'lucide-react';

const Dashboard = () => {
    const [engineId, setEngineId] = useState('ENGINE_001');
    const [twinState, setTwinState] = useState(null);
    const [replayStatus, setReplayStatus] = useState(null);
    const [explanation, setExplanation] = useState(null);
    const [history, setHistory] = useState([]);
    const [error, setError] = useState(null);

    const fetchData = async () => {
        try {
            const stateRes = await fetchTwinState(engineId);
            setTwinState(stateRes.data);
            
            const expRes = await fetchExplanation(engineId);
            setExplanation(expRes.data);

            const histRes = await fetchEngineHistory(engineId);
            setHistory(histRes.data.map(d => ({
                cycle: d.cycle,
                health: d.health_state.health_index,
                rul: d.predicted_rul,
                anomaly: d.anomaly_state.score
            })));
            
            setError(null);
        } catch (err) {
            console.error(err);
            if (err.code === "ERR_NETWORK") {
                setError("Backend Disconnected. Please ensure FastAPI is running.");
            }
        }
        
        try {
            const statusRes = await getReplayStatus();
            setReplayStatus(statusRes.data);
        } catch(e) {}
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, [engineId]);

    const handleStart = async () => {
        await startReplay(engineId);
    };

    const handleStop = async () => {
        await stopReplay();
    };

    if (error) {
        return (
            <div className="flex h-screen items-center justify-center bg-darker text-red-500 flex-col space-y-4">
                <ShieldAlert size={64} />
                <h1 className="text-2xl font-bold">SYSTEM OFFLINE</h1>
                <p>{error}</p>
                <p className="text-gray-400 text-sm max-w-md text-center">
                    Please ensure the FastAPI backend is running and the NASA C-MAPSS dataset is placed in the backend/data/ directory.
                </p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-darker text-slate-200 p-6 font-sans">
            {/* Top Bar */}
            <div className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
                <div>
                    <h1 className="text-3xl font-bold text-blue-400 tracking-wider">AeroTwin</h1>
                    <p className="text-sm text-slate-400 uppercase tracking-widest">Digital Twin Intelligence for Aero Piston Engine Health Monitoring</p>
                </div>
                <div className="flex space-x-6 text-sm">
                    <div className="flex items-center space-x-2">
                        <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
                        <span className="font-semibold text-green-400">SYSTEM ONLINE</span>
                    </div>
                    <div>
                        <span className="text-slate-500">MODEL</span> <span className="font-bold">{twinState?.model_version || 'v1.0'}</span>
                    </div>
                    <div>
                        <span className="text-slate-500">DATASET</span> <span className="font-bold">NASA C-MAPSS</span>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="flex justify-between items-center bg-slate-900 p-4 rounded-lg mb-8 shadow-lg border border-slate-800">
                <div className="flex items-center space-x-4">
                    <span className="text-slate-400">SELECT ENGINE:</span>
                    <select 
                        value={engineId} 
                        onChange={(e) => setEngineId(e.target.value)}
                        className="bg-slate-800 text-white border border-slate-600 rounded px-4 py-2 outline-none focus:border-blue-500"
                    >
                        <option value="ENGINE_001">ENGINE_001</option>
                        <option value="ENGINE_002">ENGINE_002</option>
                        <option value="ENGINE_003">ENGINE_003</option>
                    </select>
                </div>
                
                <div className="flex items-center space-x-4">
                    <div className="text-slate-400 mr-4">
                        REPLAY STATUS: 
                        <span className={`ml-2 font-bold ${replayStatus?.status === 'RUNNING' ? 'text-green-400' : 'text-yellow-400'}`}>
                            {replayStatus?.status || 'STOPPED'}
                        </span>
                    </div>
                    <button onClick={handleStart} className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded transition-colors shadow shadow-blue-900">
                        <Play size={18} /> <span>START REPLAY</span>
                    </button>
                    <button onClick={handleStop} className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-white px-6 py-2 rounded transition-colors">
                        <Square size={18} /> <span>STOP</span>
                    </button>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {/* Health */}
                <div className={`p-6 rounded-lg border shadow-lg ${
                    twinState?.health_state?.status === 'CRITICAL' ? 'bg-red-950 border-red-800' : 
                    twinState?.health_state?.status === 'WARNING' ? 'bg-orange-950 border-orange-800' : 
                    'bg-slate-900 border-slate-800'
                }`}>
                    <div className="flex items-center space-x-3 mb-2 text-slate-400">
                        <Activity size={20} /> <h3>ENGINE HEALTH</h3>
                    </div>
                    <div className="text-5xl font-bold text-white mb-2">
                        {twinState ? `${twinState.health_state.health_index}%` : '---'}
                    </div>
                    <div className={`text-sm font-semibold tracking-wider ${
                        twinState?.health_state?.status === 'NORMAL' ? 'text-green-400' :
                        twinState?.health_state?.status === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                        STATUS: {twinState?.health_state?.status || 'UNKNOWN'}
                    </div>
                </div>

                {/* RUL */}
                <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TrendingDown size={64} />
                    </div>
                    <div className="text-slate-400 mb-2 tracking-wider text-sm">PREDICTED RUL</div>
                    <div className="text-5xl font-bold text-white mb-2">
                        {twinState ? twinState.predicted_rul : '---'}
                        <span className="text-xl text-slate-500 ml-2">cycles</span>
                    </div>
                    <div className="text-xs text-slate-500 mt-4 border-t border-slate-800 pt-2">
                        BASED ON RANDOM FOREST REGRESSOR
                    </div>
                </div>

                {/* Anomaly */}
                <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                    <div className="flex items-center space-x-3 mb-2 text-slate-400">
                        <AlertTriangle size={20} /> <h3 className="tracking-wider text-sm">ANOMALY SCORE</h3>
                    </div>
                    <div className={`text-4xl font-bold mb-2 ${twinState?.anomaly_state?.flag ? 'text-red-400' : 'text-white'}`}>
                        {twinState ? twinState.anomaly_state.score : '---'}
                    </div>
                    <div className="text-sm text-slate-400">
                        Severity: <span className="font-bold text-white">{twinState?.anomaly_state?.severity || '---'}</span>
                    </div>
                </div>

                {/* Degradation */}
                <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                    <div className="text-slate-400 mb-2 tracking-wider text-sm">DEGRADATION TREND</div>
                    <div className="text-3xl font-bold text-white mt-4">
                        {twinState?.degradation_state?.trend || '---'}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Charts */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Health Chart */}
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                        <h3 className="text-lg font-semibold mb-6 text-slate-300">Health Index Trend</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer>
                                <LineChart data={history}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                    <XAxis dataKey="cycle" stroke="#64748b" />
                                    <YAxis domain={[0, 100]} stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                    <Line type="monotone" dataKey="health" stroke="#3b82f6" strokeWidth={2} dot={false} isAnimationActive={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    
                    {/* RUL Chart */}
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                        <h3 className="text-lg font-semibold mb-6 text-slate-300">Remaining Useful Life (RUL) Prediction</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer>
                                <LineChart data={history}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                    <XAxis dataKey="cycle" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                    <Line type="stepAfter" dataKey="rul" stroke="#8b5cf6" strokeWidth={2} dot={false} isAnimationActive={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Side Panel */}
                <div className="space-y-8">
                    {/* Digital Twin State */}
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                        <h3 className="text-lg font-semibold mb-4 text-slate-300 border-b border-slate-700 pb-2">DIGITAL TWIN STATE</h3>
                        {twinState ? (
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between"><span className="text-slate-500">ID:</span> <span className="font-mono text-blue-300">{twinState.engine_id}</span></div>
                                <div className="flex justify-between"><span className="text-slate-500">CYCLE:</span> <span className="font-mono text-white">{twinState.cycle}</span></div>
                                <div className="flex justify-between"><span className="text-slate-500">UPDATE:</span> <span className="font-mono text-slate-400">{new Date(twinState.last_update).toLocaleTimeString()}</span></div>
                                <div className="flex justify-between"><span className="text-slate-500">SYNC:</span> <span className="font-semibold text-green-400">LIVE STREAM</span></div>
                            </div>
                        ) : (
                            <div className="text-slate-500">Waiting for data...</div>
                        )}
                    </div>

                    {/* Explainability */}
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                        <div className="flex items-center space-x-2 mb-4 border-b border-slate-700 pb-2">
                            <Info size={18} className="text-blue-400"/>
                            <h3 className="text-lg font-semibold text-slate-300">WHY WAS THIS ALERT GENERATED?</h3>
                        </div>
                        {explanation ? (
                            <div className="space-y-4 mt-4">
                                <p className="text-xs text-slate-400 mb-2">Top Contributing Sensors:</p>
                                {explanation.top_contributors.map((c, i) => (
                                    <div key={i} className="mb-2">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-mono text-slate-300">{c.feature}</span>
                                            <span className="text-slate-400">{Math.round(c.importance * 100)}%</span>
                                        </div>
                                        <div className="w-full bg-slate-800 rounded-full h-2">
                                            <div className="bg-red-500 h-2 rounded-full" style={{ width: `${Math.min(100, c.importance * 200)}%` }}></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-slate-500">No anomaly explanation available.</div>
                        )}
                    </div>

                    {/* Sensor Data */}
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-lg">
                        <h3 className="text-lg font-semibold mb-4 text-slate-300 border-b border-slate-700 pb-2">LIVE SENSOR TELEMETRY</h3>
                        <div className="h-64 overflow-y-auto pr-2 space-y-2">
                            {twinState?.sensor_state ? (
                                Object.entries(twinState.sensor_state).slice(0, 10).map(([sensor, val]) => (
                                    <div key={sensor} className="flex justify-between items-center p-2 bg-slate-800 rounded border border-slate-700">
                                        <span className="font-mono text-sm text-slate-300">{sensor}</span>
                                        <span className="font-mono font-bold text-blue-300">{val.toFixed(4)}</span>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500">No telemetry stream.</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Disclaimer */}
            <div className="mt-12 text-center text-xs text-slate-600 border-t border-slate-800 pt-6">
                <p>This is a research/demo prototype validating the predictive-health-monitoring architecture using public aerospace prognostics data (NASA C-MAPSS).</p>
                <p>It is not certified for operational aircraft decisions. Do not use for physical MALE UAV piston engine diagnosis without physical retraining.</p>
            </div>
        </div>
    );
};

export default Dashboard;
