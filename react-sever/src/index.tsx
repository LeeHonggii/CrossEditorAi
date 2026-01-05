import './polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import './styles/styleguide.css';
import App from './App';

console.log("Index.tsx running");
const rootElement = document.getElementById('root');
console.log("Root element:", rootElement);

ReactDOM.render(<App />, document.getElementById('root'));
