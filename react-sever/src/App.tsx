import React, { Suspense } from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import "./styles/Global.css";
import Main from "./pages/Main";
// Lazy load other components
const Upload = React.lazy(() => import("./pages/Upload"));
const Loading = React.lazy(() => import("./pages/Loading"));
const Result = React.lazy(() => import("./pages/Result"));
const Manual = React.lazy(() => import("./pages/Manual"));

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={<div style={{ color: 'white', textAlign: 'center', marginTop: '50px' }}>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/loading" element={<Loading />} />
          <Route path="/manual" element={<Manual />} />
          <Route path="/result" element={<Result />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;
