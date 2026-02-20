import { Link } from 'react-router-dom';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer w-full flex-shrink-0">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col items-center md:items-start">
            <p className="site-footer-title">Тет-а-Тет</p>
            <p className="site-footer-text text-sm">
              &copy; {currentYear} Конструктор рам. Все права защищены.
            </p>
          </div>
          <div className="flex space-x-6">
            <Link
              to="/"
              className="site-footer-link"
            >
              Создать заказ
            </Link>
            <Link
              to="/cabinet"
              className="site-footer-link"
            >
              Мой кабинет
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
