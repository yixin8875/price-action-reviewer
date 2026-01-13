import { useState, useMemo } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { lightTheme, darkTheme } from './theme';
import { useAuthStore } from './stores/authStore';
import ErrorBoundary from './components/ErrorBoundary';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Instruments from './pages/Instruments';
import Charts from './pages/Charts';
import Reviews from './pages/Reviews';
import ReviewForm from './pages/Reviews/ReviewForm';
import Indicators from './pages/Indicators';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const theme = useMemo(() => (darkMode ? darkTheme : lightTheme), [darkMode]);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <Dashboard />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/instruments"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <Instruments />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/charts"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <Charts />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/reviews"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <Reviews />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/reviews/new"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <ReviewForm />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/reviews/:id/edit"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <ReviewForm />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/indicators"
                element={
                  <PrivateRoute>
                    <MainLayout darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)}>
                      <Indicators />
                    </MainLayout>
                  </PrivateRoute>
                }
              />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
