import React, { useState, useMemo } from "react";
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Select,
  Flex,
  HStack,
  Text,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from "@chakra-ui/react";
import { ChevronUpIcon, ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';

const TransactionEntry = ({ transactions, cardBg, textColor }) => {
  const [sortField, setSortField] = useState("txn_date");
  const [sortDirection, setSortDirection] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState("10");

  {/* Sort Control */}
  const toggleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

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

  {/* Pagination Control */}
  const totalPages = useMemo(() => {
    if (itemsPerPage === 'all') return 1;
    return Math.ceil(transactions.length / Number(itemsPerPage));
  }, [transactions, itemsPerPage]);

  const currentTransactions = useMemo(() => {
    const sortedTransactions = sortTransactions(transactions);
    if (itemsPerPage === 'all') return sortedTransactions;
    const startIndex = (currentPage - 1) * Number(itemsPerPage);
    return sortedTransactions.slice(startIndex, startIndex + Number(itemsPerPage));
  }, [transactions, currentPage, itemsPerPage, sortField, sortDirection]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleItemsPerPageChange = (event) => {
    setItemsPerPage(event.target.value);
    setCurrentPage(1);
  };

  return (
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
  );
};

export default TransactionEntry;