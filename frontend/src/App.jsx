import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { OrderProvider } from './context/OrderContext';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Wizard } from './pages/Wizard';
import { Summary } from './pages/Summary';
import { Cabinet } from './pages/Cabinet';
import './App.css';

function App() {
  return (
    <OrderProvider>
      <BrowserRouter>
        <div className="h-full flex flex-col">
          <Header />
          <main className="flex-1 overflow-y-auto pt-8">
            <Routes>
              <Route path="/" element={<Wizard />} />
              <Route path="/summary" element={<Summary />} />
              <Route path="/cabinet" element={<Cabinet />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </OrderProvider>
  );
}

export default App;
