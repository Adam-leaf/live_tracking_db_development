import React, { useState, useRef, useEffect } from "react";
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
} from "@chakra-ui/react";
import TransactionEntry from "../components/tier2/TransactionEntry";

const AssetTabs = ({ tokenData, pic, exchange }) => {

  {/* Colour */}
  const bgColor = useColorModeValue("gray.50", "gray.900");
  const cardBg = useColorModeValue("white", "gray.800");
  const tabBg = useColorModeValue("gray.100", "gray.700");
  const activeTabBg = useColorModeValue("white", "gray.600");
  const textColor = useColorModeValue("gray.800", "gray.100");
  const scrollbarThumbColor = useColorModeValue(
    "rgba(0,0,0,0.3)",
    "rgba(255,255,255,0.3)"
  );
  const scrollbarTrackColor = useColorModeValue(
    "rgba(0,0,0,0.1)",
    "rgba(255,255,255,0.1)"
  );

  {/* Variables */}
  const tokens = Object.keys(tokenData);
  const [currentToken, setCurrentToken] = useState(tokens[0]);
  const [showTransactions, setShowTransactions] = useState(false);
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);
  const tabListRef = useRef(null);

  useEffect(() => {
    setSelectedTabIndex(0);
  }, [pic, exchange]);

  const isScrollable = tokens.length > 10;

  {/* Tab Control */}
  const handleTabChange = (index) => {
    setSelectedTabIndex(index);
    setCurrentToken(tokens[index]);
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

        <Tabs
          variant="soft-rounded"
          colorScheme="blue"
          index={selectedTabIndex}
          onChange={handleTabChange}
        >
          <Box
            bg={tabBg}
            borderRadius="full"
            pt={2}
            px={2}
            mb={6}
            position="relative"
            overflow="hidden"
          >
            <TabList
              ref={tabListRef}
              overflowX={isScrollable ? "auto" : "visible"}
              overflowY="hidden"
              whiteSpace="nowrap"
              css={{
                "&::-webkit-scrollbar": {
                  height: "8px",
                  marginTop: "8px",
                },
                "&::-webkit-scrollbar-thumb": {
                  backgroundColor: scrollbarThumbColor,
                  borderRadius: "4px",
                  border: "2px solid transparent",
                  backgroundClip: "padding-box",
                },
                "&::-webkit-scrollbar-track": {
                  backgroundColor: scrollbarTrackColor,
                  borderRadius: "4px",
                  margin: "0 16px",
                },
                scrollbarWidth: "thin",
                scrollbarColor: `${scrollbarThumbColor} ${scrollbarTrackColor}`,
                paddingBottom: "8px",
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

          <TabPanels>
            {tokens.map((token) => (
              <TabPanel key={token} p={0}>
                <VStack spacing={6} align="stretch">
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
                            <Td
                              isNumeric
                              color={item.PnL >= 0 ? "green.500" : "red.500"}
                            >
                              {item.PnL.toFixed(2)}
                            </Td>
                            <Td isNumeric>
                              {item["Current Balance"].toFixed(2)}
                            </Td>
                            <Td isNumeric>{item["USD Value"].toFixed(2)}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>

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
                        {tokenData[token].pnl_verification.map(
                          (item, index) => (
                            <Tr key={index}>
                              <Td isNumeric>{item["Bal USD"].toFixed(2)}</Td>
                              <Td isNumeric>{item["In Amount"].toFixed(2)}</Td>
                              <Td isNumeric>{item["Out Amount"].toFixed(2)}</Td>
                              <Td
                                isNumeric
                                color={
                                  item.Difference >= 0 ? "green.500" : "red.500"
                                }
                              >
                                {item.Difference.toFixed(2)}
                              </Td>
                              <Td
                                isNumeric
                                color={
                                  item["Total PNL"] >= 0
                                    ? "green.500"
                                    : "red.500"
                                }
                              >
                                {item["Total PNL"].toFixed(2)}
                              </Td>
                            </Tr>
                          )
                        )}
                      </Tbody>
                    </Table>
                  </Box>

                  <Button
                    onClick={() => setShowTransactions(!showTransactions)}
                    colorScheme="blue"
                    variant="outline"
                  >
                    {showTransactions ? "Hide" : "Show"} Transaction History
                  </Button>

                  {showTransactions && (
                    <TransactionEntry
                      transactions={tokenData[token].transactions}
                      cardBg={cardBg}
                      textColor={textColor}
                    />
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
