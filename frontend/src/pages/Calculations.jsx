import React, { useState, useEffect } from 'react';
import { Text, Box, useColorModeValue, Select, Spinner, Center } from "@chakra-ui/react";
import AssetTabs from "../components/AssetTabs";

const Calculations = () => {
  const [pnlData, setPnlData] = useState(null);
  const [selectedPIC, setSelectedPIC] = useState('');
  const [selectedExchange, setSelectedExchange] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPnlData = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://127.0.0.1:5001/calc_pnl');
        const data = await response.json();
        setPnlData(data);
        if (data.pic && Object.keys(data.pic).length > 0) {
          setSelectedPIC(Object.keys(data.pic)[0]);
          const firstPIC = Object.keys(data.pic)[0];
          if (data.pic[firstPIC].exchanges && Object.keys(data.pic[firstPIC].exchanges).length > 0) {
            setSelectedExchange(Object.keys(data.pic[firstPIC].exchanges)[0]);
          }
        }
      } catch (error) {
        console.error('Error fetching PnL data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPnlData();
  }, []);

  const handlePICChange = (event) => {
    setSelectedPIC(event.target.value);
    if (pnlData.pic[event.target.value].exchanges) {
      setSelectedExchange(Object.keys(pnlData.pic[event.target.value].exchanges)[0]);
    } else {
      setSelectedExchange('');
    }
  };

  const handleExchangeChange = (event) => {
    setSelectedExchange(event.target.value);
  };

  return (
    <>
      <Box p={4} my={4} borderRadius={5} bg={useColorModeValue("gray.200", "gray.700")}>
        <Text fontSize="2xl" as="b">Spot PnL</Text>
      </Box>

      {isLoading ? (
        <Center h="200px">
          <Spinner size="xl" color="blue.500" thickness="4px" />
        </Center>
      ) : pnlData ? (
        <Box p={4} my={4} borderRadius={5} bg={useColorModeValue("gray.200", "gray.700")}>
          <Select placeholder="Select PIC" value={selectedPIC} onChange={handlePICChange} mb={4}>
            {Object.keys(pnlData.pic).map((pic) => (
              <option key={pic} value={pic}>{pic}</option>
            ))}
          </Select>

          {selectedPIC && (
            <Select placeholder="Select Exchange" value={selectedExchange} onChange={handleExchangeChange} mb={4}>
              {Object.keys(pnlData.pic[selectedPIC].exchanges).map((exchange) => (
                <option key={exchange} value={exchange}>{exchange}</option>
              ))}
            </Select>
          )}

          {selectedPIC && selectedExchange && (
            <AssetTabs
              tokenData={pnlData.pic[selectedPIC].exchanges[selectedExchange].tokens} 
              pic={selectedPIC}
              exchange={selectedExchange}
            />
          )}
        </Box>
      ) : (
        <Text>No data available. Please try again later.</Text>
      )}
    </>
  );
};

export default Calculations;