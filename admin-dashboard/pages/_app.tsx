import React from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';

function BeeMindApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default BeeMindApp;
