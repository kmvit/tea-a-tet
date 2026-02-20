import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Header = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="site-header">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link to="/" className="site-logo">
            <span className="site-logo-mark" aria-hidden="true" />
            <span className="flex flex-col">
              <span className="site-logo-title">Тет-а-Тет</span>
              <span className="site-logo-subtitle">Конструктор рам</span>
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-3">
            <Link
              to="/"
              className={`site-nav-link ${
                isActive('/') || location.pathname.startsWith('/step')
                  ? 'site-nav-link--active'
                  : ''
              }`}
            >
              Создать заказ
            </Link>
            <Link
              to="/cabinet"
              className={`site-nav-link ${
                isActive('/cabinet')
                  ? 'site-nav-link--active'
                  : ''
              }`}
            >
              Мой кабинет
            </Link>
          </nav>
          
          {/* Mobile menu button */}
          <button
            id="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-700 hover:text-blue-600 focus:outline-none"
            aria-label="Меню"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
              />
            </svg>
          </button>
        </div>
        
        {/* Mobile Navigation */}
        <div
          className={`md:hidden pb-4 border-t border-gray-200/70 mt-2 transition-all duration-300 ${
            mobileMenuOpen ? 'block' : 'hidden'
          }`}
        >
          <nav className="flex flex-col space-y-2 pt-4">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className={`site-nav-link ${
                isActive('/') || location.pathname.startsWith('/step')
                  ? 'site-nav-link--active'
                  : ''
              }`}
            >
              Создать заказ
            </Link>
            <Link
              to="/cabinet"
              onClick={() => setMobileMenuOpen(false)}
              className={`site-nav-link ${
                isActive('/cabinet')
                  ? 'site-nav-link--active'
                  : ''
              }`}
            >
              Мой кабинет
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};
