import React from 'react';
import Head from 'next/head';
import Dashboard from '../components/Dashboard';

const HomePage: React.FC = () => {
  return (
    <>
      <Head>
        <title>BeeMind Dashboard - AI Evolution Monitoring</title>
        <meta name="description" content="BeeMind AI Evolution Dashboard - Monitor drone activity, blockchain integrity, and model performance in real-time" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Dashboard />
    </>
  );
};

export default HomePage;
