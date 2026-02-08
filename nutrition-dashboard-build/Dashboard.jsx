import React, { useState } from 'react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';

const NutritionDashboard = () => {
  const [weekData, setWeekData] = useState([
    { day: 'Mon', calories: 1840, protein: 173, carbs: 126, fat: 69, weight: 225.2 },
    { day: 'Tue', calories: 2138, protein: 208, carbs: 119, fat: 88, weight: 224.8 },
    { day: 'Wed', calories: 1630, protein: 91, carbs: 154, fat: 11, weight: 225.1 },
    { day: 'Thu', calories: 2100, protein: 195, carbs: 240, fat: 65, weight: 224.9 },
    { day: 'Fri', calories: 1875, protein: 128, carbs: 111, fat: 100, weight: 224.5 },
    { day: 'Sat', calories: 2050, protein: 180, carbs: 210, fat: 72, weight: 224.3 },
    { day: 'Sun', calories: 0, protein: 0, carbs: 0, fat: 0, weight: 224.2 },
  ]);

  const [editingDay, setEditingDay] = useState(null);
  const [editValues, setEditValues] = useState({});

  // Calculate stats
  const validDays = weekData.filter(d => d.calories > 0);
  const avgCalories = Math.round(validDays.reduce((sum, d) => sum + d.calories, 0) / validDays.length);
  const avgProtein = Math.round(validDays.reduce((sum, d) => sum + d.protein, 0) / validDays.length);
  const startWeight = validDays[0]?.weight || 0;
  const endWeight = validDays[validDays.length - 1]?.weight || 0;
  const weightChange = (endWeight - startWeight).toFixed(1);
  const weightTrend = weightChange < 0 ? '↓' : weightChange > 0 ? '↑' : '→';

  // Macro split for pie chart
  const totalMacros = validDays.reduce((acc, d) => ({
    protein: acc.protein + d.protein,
    carbs: acc.carbs + d.carbs,
    fat: acc.fat + d.fat
  }), { protein: 0, carbs: 0, fat: 0 });

  const macroData = [
    { name: 'Protein', value: totalMacros.protein, color: '#3b82f6' },
    { name: 'Carbs', value: totalMacros.carbs, color: '#10b981' },
    { name: 'Fat', value: totalMacros.fat, color: '#ef4444' }
  ];

  const handleEditRow = (day) => {
    setEditingDay(day.day);
    setEditValues({ ...day });
  };

  const handleSaveRow = () => {
    setWeekData(weekData.map(d => d.day === editingDay ? editValues : d));
    setEditingDay(null);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Nutrition</h1>
        <p className="text-gray-400">Week of Feb 2-8</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <p className="text-gray-400 text-sm mb-2">Avg Calories</p>
          <p className="text-3xl font-bold text-amber-400">{avgCalories}</p>
          <p className="text-gray-500 text-xs mt-2">Target: 2,200</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <p className="text-gray-400 text-sm mb-2">Avg Protein</p>
          <p className="text-3xl font-bold text-blue-400">{avgProtein}g</p>
          <p className="text-gray-500 text-xs mt-2">Target: 200g</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <p className="text-gray-400 text-sm mb-2">Weight Change</p>
          <p className="text-3xl font-bold text-purple-400">{weightTrend} {Math.abs(weightChange)}lb</p>
          <p className="text-gray-500 text-xs mt-2">{startWeight} → {endWeight}</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Calorie Bar Chart */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Daily Calories</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="day" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                formatter={(value) => `${value} cal`}
              />
              <Bar dataKey="calories" fill="#f59e0b" />
              <Bar dataKey="calories" fill="#f59e0b" stroke="#fbbf24" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Macro Pie Chart */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Macro Split (Week Total)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={macroData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}g`} outerRadius={80}>
                {macroData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Macro Trend Area Chart */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Macro Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="day" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Area type="monotone" dataKey="protein" fill="#3b82f6" stroke="#3b82f6" fillOpacity={0.3} />
              <Area type="monotone" dataKey="carbs" fill="#10b981" stroke="#10b981" fillOpacity={0.3} />
              <Area type="monotone" dataKey="fat" fill="#ef4444" stroke="#ef4444" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Weight Trend Line Chart */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Weight Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="day" stroke="#666" />
              <YAxis stroke="#666" domain={[224, 226]} />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Line type="monotone" dataKey="weight" stroke="#a855f7" strokeWidth={2} dot={{ fill: '#a855f7', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Editable Daily Log Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Daily Log</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-800">
              <tr className="text-left text-gray-400">
                <th className="pb-3 font-semibold">Day</th>
                <th className="pb-3 font-semibold text-amber-400">Calories</th>
                <th className="pb-3 font-semibold text-blue-400">Protein</th>
                <th className="pb-3 font-semibold text-green-400">Carbs</th>
                <th className="pb-3 font-semibold text-red-400">Fat</th>
                <th className="pb-3 font-semibold text-purple-400">Weight</th>
                <th className="pb-3"></th>
              </tr>
            </thead>
            <tbody>
              {weekData.map((day) => (
                <tr key={day.day} className="border-b border-gray-800 hover:bg-gray-800 transition">
                  {editingDay === day.day ? (
                    <>
                      <td className="py-3">{day.day}</td>
                      <td><input type="number" value={editValues.calories} onChange={(e) => setEditValues({ ...editValues, calories: parseInt(e.target.value) })} className="bg-gray-800 text-amber-400 w-20 px-2 py-1 rounded" /></td>
                      <td><input type="number" value={editValues.protein} onChange={(e) => setEditValues({ ...editValues, protein: parseInt(e.target.value) })} className="bg-gray-800 text-blue-400 w-20 px-2 py-1 rounded" /></td>
                      <td><input type="number" value={editValues.carbs} onChange={(e) => setEditValues({ ...editValues, carbs: parseInt(e.target.value) })} className="bg-gray-800 text-green-400 w-20 px-2 py-1 rounded" /></td>
                      <td><input type="number" value={editValues.fat} onChange={(e) => setEditValues({ ...editValues, fat: parseInt(e.target.value) })} className="bg-gray-800 text-red-400 w-20 px-2 py-1 rounded" /></td>
                      <td><input type="number" step="0.1" value={editValues.weight} onChange={(e) => setEditValues({ ...editValues, weight: parseFloat(e.target.value) })} className="bg-gray-800 text-purple-400 w-20 px-2 py-1 rounded" /></td>
                      <td><button onClick={handleSaveRow} className="text-green-400 hover:text-green-300 font-semibold">Save</button></td>
                    </>
                  ) : (
                    <>
                      <td className="py-3 font-medium">{day.day}</td>
                      <td className="text-amber-400">{day.calories > 0 ? day.calories : '—'}</td>
                      <td className="text-blue-400">{day.protein > 0 ? day.protein : '—'}</td>
                      <td className="text-green-400">{day.carbs > 0 ? day.carbs : '—'}</td>
                      <td className="text-red-400">{day.fat > 0 ? day.fat : '—'}</td>
                      <td className="text-purple-400">{day.weight > 0 ? day.weight : '—'}</td>
                      <td><button onClick={() => handleEditRow(day)} className="text-gray-400 hover:text-gray-200 font-semibold">Edit</button></td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default NutritionDashboard;
