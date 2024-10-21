import React, { useState, useMemo, useRef, useEffect } from "react";
import {
  Box,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Heading,
  VStack,
  HStack,
  Badge,
  Button,
  Select,
  Flex,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from "@chakra-ui/react";
import { ChevronUpIcon, ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';

const AssetTabs = ({ tokenData, pic, exchange }) => {

  {/* Colour */}
  const bgColor = useColorModeValue("gray.50", "gray.900");
  const cardBg = useColorModeValue("white", "gray.800");
  const tabBg = useColorModeValue("gray.100", "gray.700");
  const activeTabBg = useColorModeValue("white", "gray.600");
  const textColor = useColorModeValue("gray.800", "gray.100");
  const scrollbarThumbColor = useColorModeValue("rgba(0,0,0,0.3)", "rgba(255,255,255,0.3)");
  const scrollbarTrackColor = useColorModeValue("rgba(0,0,0,0.1)", "rgba(255,255,255,0.1)");

  {/* Variables */}
  const tokens = Object.keys(tokenData);
  const [currentToken, setCurrentToken] = useState(tokens[0]);
  const [showTransactions, setShowTransactions] = useState(false);
  const [sortField, setSortField] = useState("txn_date");
  const [sortDirection, setSortDirection] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState("10");
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);
  const tabListRef = useRef(null);

  // Reset currentPage to 1 when pic or exchange changes
  useEffect(() => {
    setSelectedTabIndex(0);
    setCurrentPage(1);
  }, [pic, exchange]); 

  {/* Scroll Control */}
  useEffect(() => {
    const checkScrollability = () => {
      if (tabListRef.current) {
        const { scrollLeft, scrollWidth, clientWidth } = tabListRef.current;
        setCanScrollLeft(scrollLeft > 0);
        setCanScrollRight(scrollLeft + clientWidth < scrollWidth);
      }
    };

    checkScrollability();
    window.addEventListener('resize', checkScrollability);
    return () => window.removeEventListener('resize', checkScrollability);
  }, []);

  const isScrollable = tokens.length > 10;

  {/* Sort Control */}
  const sortTransactions = (transactions) => {
    return [...transactions].sort((a, b) => {
      if (sortField === "usd_value") {
        return sortDirection === "asc" ? a.usd_value - b.usd_value : b.usd_value - a.usd_value;
      } else {
        return sortDirection === "asc" 
          ? new Date(a.txn_date) - new Date(b.txn_date) 
          : new Date(b.txn_date) - new Date(a.txn_date);
      }
    });
  };

  const toggleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  {/* Pagination Control */}
  const totalPages = useMemo(() => {
    if (itemsPerPage === 'all') return 1;
    return Math.ceil(tokenData[currentToken].transactions.length / Number(itemsPerPage));
  }, [tokenData, currentToken, itemsPerPage]);

  const currentTransactions = useMemo(() => {
    const transactions = sortTransactions(tokenData[currentToken].transactions);
    if (itemsPerPage === 'all') return transactions;
    const startIndex = (currentPage - 1) * Number(itemsPerPage);
    return transactions.slice(startIndex, startIndex + Number(itemsPerPage));
  }, [tokenData, currentToken, currentPage, itemsPerPage, sortField, sortDirection]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleItemsPerPageChange = (event) => {
    setItemsPerPage(event.target.value);
    setCurrentPage(1);
  };

  const handleTabChange = (index) => {
    setSelectedTabIndex(index);
    setCurrentToken(tokens[index]);
    setCurrentPage(1);  // Reset to first page when changing tokens
  };

  return (
    <Box bg={bgColor} p={6} borderRadius="xl" boxShadow="xl">
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <Heading size="lg" color={textColor}>
          Asset Overview
        </Heading>
        <HStack>
          <Badge colorScheme="purple">PIC: {pic}</Badge>
          <Badge colorScheme="green">Exchange: {exchange}</Badge>
        </HStack>
      </HStack>

      <Tabs variant="soft-rounded" colorScheme="blue" index={selectedTabIndex} onChange={handleTabChange}>
          <Box 
            bg={tabBg}
            borderRadius="full"
            pt={2}
            px={2}
            mb={6}
            position="relative"
            overflow="hidden"
          >
            
            {/* Tab headers */}
            <TabList 
              overflowX={isScrollable ? "auto" : "visible"}
              overflowY="hidden"
              whiteSpace="nowrap"
              css={{
                '&::-webkit-scrollbar': {
                  height: '8px',
                  marginTop: '8px', 
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: scrollbarThumbColor,
                  borderRadius: '4px',
                  border: '2px solid transparent',
                  backgroundClip: 'padding-box',
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: scrollbarTrackColor,
                  borderRadius: '4px',
                  margin: '0 16px',  // Add horizontal margin to the track
                },
                'scrollbarWidth': 'thin',
                'scrollbarColor': `${scrollbarThumbColor} ${scrollbarTrackColor}`,
                'paddingBottom': '8px',  // Add padding to the bottom of the TabList
              }}
            >
              {tokens.map((token) => (
                <Tab
                  key={token}
                  _selected={{ bg: activeTabBg, color: "blue.500" }}
                  borderRadius="full"
                  px={4}
                  py={2}
                  mr={2}
                >
                  {token}
                </Tab>
              ))}
            </TabList>
          </Box>
          
          {/* Tab Content */}
          <TabPanels>
            {tokens.map((token) => (
              <TabPanel key={token} p={0}>
                <VStack spacing={6} align="stretch">
                  {/* PnL Breakdown */}
                  <Box bg={cardBg} p={6} borderRadius="lg" boxShadow="md">
                    <Heading size="md" mb={4} color={textColor}>
                      PnL Breakdown
                    </Heading>
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th>Type</Th>
                          <Th>Position</Th>
                          <Th isNumeric>PnL</Th>
                          <Th isNumeric>Current Balance</Th>
                          <Th isNumeric>USD Value</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {tokenData[token].pnl.map((item, index) => (
                          <Tr key={index}>
                            <Td>{item["PnL Type"]}</Td>
                            <Td>{item.Position}</Td>
                            <Td isNumeric color={item.PnL >= 0 ? "green.500" : "red.500"}>
                              {item.PnL.toFixed(2)}
                            </Td>
                            <Td isNumeric>{item["Current Balance"].toFixed(2)}</Td>
                            <Td isNumeric>{item["USD Value"].toFixed(2)}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                  
                  {/* PnL Verification */}
                  <Box bg={cardBg} p={6} borderRadius="lg" boxShadow="md">
                    <Heading size="md" mb={4} color={textColor}>
                      PnL Verification
                    </Heading>
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th isNumeric>Balance (USD)</Th>
                          <Th isNumeric>In Amount</Th>
                          <Th isNumeric>Out Amount</Th>
                          <Th isNumeric>Amount Change</Th>
                          <Th isNumeric>Total PnL</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {tokenData[token].pnl_verification.map((item, index) => (
                          <Tr key={index}>
                            <Td isNumeric>{item["Bal USD"].toFixed(2)}</Td>
                            <Td isNumeric>{item["In Amount"].toFixed(2)}</Td>
                            <Td isNumeric>{item["Out Amount"].toFixed(2)}</Td>
                            <Td isNumeric color={item.Difference >= 0 ? "green.500" : "red.500"}>
                              {item.Difference.toFixed(2)}
                            </Td>
                            <Td isNumeric color={item["Total PNL"] >= 0 ? "green.500" : "red.500"}>
                              {item["Total PNL"].toFixed(2)}
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                  
                  {/* Transaction History Toggle */}
                  <Button 
                    onClick={() => setShowTransactions(!showTransactions)}
                    colorScheme="blue"
                    variant="outline"
                  >
                    {showTransactions ? "Hide" : "Show"} Transaction History
                  </Button>

                  {/* Transaction History */}
                  {showTransactions && (
                    <Box bg={cardBg} p={6} borderRadius="lg" boxShadow="md">
                      <Heading size="md" mb={4} color={textColor}>
                        Transaction History
                      </Heading>
                      <HStack mb={4} justify="space-between" wrap="wrap">
                        <HStack>
                          <Text>Sort by:</Text>
                          <Select 
                            value={sortField} 
                            onChange={(e) => toggleSort(e.target.value)}
                            size="sm"
                            width="auto"
                          >
                            <option value="txn_date">Date</option>
                            <option value="usd_value">USD Value</option>
                          </Select>
                          <Button
                            onClick={() => setSortDirection(sortDirection === "asc" ? "desc" : "asc")}
                            size="sm"
                            leftIcon={sortDirection === "asc" ? <ChevronUpIcon /> : <ChevronDownIcon />}
                          >
                            {sortDirection === "asc" ? "Ascending" : "Descending"}
                          </Button>
                        </HStack>
                        <HStack>
                          <Text>Items per page:</Text>
                          <Select
                            value={itemsPerPage}
                            onChange={handleItemsPerPageChange}
                            size="sm"
                            width="auto"
                          >
                            <option value="10">10</option>
                            <option value="25">25</option>
                            <option value="50">50</option>
                            <option value="all">All</option>
                          </Select>
                        </HStack>
                      </HStack>
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th isNumeric>Exchange ID</Th>
                            <Th isNumeric>
                              <HStack spacing={1} justify="flex-end">
                                <Text>Date</Text>
                                {sortField === "txn_date" && (
                                  sortDirection === "asc" ? <ChevronUpIcon /> : <ChevronDownIcon />
                                )}
                              </HStack>
                            </Th>
                            <Th isNumeric>Exchange</Th>
                            <Th isNumeric>PIC</Th>
                            <Th isNumeric>Position</Th>
                            <Th isNumeric>Type</Th>
                            <Th isNumeric>Amount</Th>
                            <Th isNumeric>Price</Th>
                            <Th isNumeric>
                              <HStack spacing={1} justify="flex-end">
                                <Text>USD Value</Text>
                                {sortField === "usd_value" && (
                                  sortDirection === "asc" ? <ChevronUpIcon /> : <ChevronDownIcon />
                                )}
                              </HStack>
                            </Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {currentTransactions.map((item, index) => (
                            <Tr key={index}>
                              <Td isNumeric>{item.exchange_id}</Td>
                              <Td isNumeric>{item.txn_date}</Td>
                              <Td isNumeric>{item.exchange}</Td>
                              <Td isNumeric>{item.pic}</Td>
                              <Td isNumeric>{item.position}</Td>
                              <Td isNumeric>{item.txn_type}</Td>
                              <Td isNumeric>{item.token_amt}</Td>
                              <Td isNumeric>{item.token_price}</Td>
                              <Td isNumeric>{item.usd_value.toFixed(2)}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                      {itemsPerPage !== 'all' && (
                        <Flex justify="space-between" align="center" mt={4}>
                          <Text>
                            Page {currentPage} of {totalPages}
                          </Text>
                          <HStack>
                            <Button
                              onClick={() => handlePageChange(currentPage - 1)}
                              isDisabled={currentPage === 1}
                              size="sm"
                            >
                              <ChevronLeftIcon />
                            </Button>
                            <NumberInput
                              min={1}
                              max={totalPages}
                              value={currentPage}
                              onChange={(_, value) => handlePageChange(value)}
                              size="sm"
                              maxW={20}
                            >
                              <NumberInputField />
                              <NumberInputStepper>
                                <NumberIncrementStepper />
                                <NumberDecrementStepper />
                              </NumberInputStepper>
                            </NumberInput>
                            <Button
                              onClick={() => handlePageChange(currentPage + 1)}
                              isDisabled={currentPage === totalPages}
                              size="sm"
                            >
                              <ChevronRightIcon />
                            </Button>
                          </HStack>
                        </Flex>
                      )}
                    </Box>
                  )}
                </VStack>
              </TabPanel>
            ))}
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default AssetTabs;