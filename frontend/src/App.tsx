import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './pages/SearchPage';
import ResultsPage from './pages/ResultsPage';
import JobSearchPage from './pages/JobSearchPage';
import JobDetailsPage from './pages/JobDetailsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import UserProfilePage from './pages/UserProfilePage';
import { Layout } from './components/Layout';
import './i18n/index';
import './styles/global.css';
import './styles/custom.css';
import './styles/mobile-responsive.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Layout><SearchPage /></Layout>} />
          <Route path="/search" element={<Layout><JobSearchPage /></Layout>} />
          <Route path="/results" element={<Layout><ResultsPage /></Layout>} />
          <Route path="/jobs/:id" element={<Layout><JobDetailsPage /></Layout>} />
          <Route path="/login" element={<Layout><LoginPage /></Layout>} />
          <Route path="/register" element={<Layout><RegisterPage /></Layout>} />
          <Route path="/forgot-password" element={<Layout><ForgotPasswordPage /></Layout>} />
          <Route path="/profile" element={<Layout><UserProfilePage /></Layout>} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;