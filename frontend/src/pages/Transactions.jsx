import { Text, Box, useColorModeValue, Button, HStack, Select } from "@chakra-ui/react";
import { useState, useEffect, useMemo } from 'react';
import axios from "axios";

/* Components */
import TransactionTable from "../components/TransactionTable";

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await axios.get(
          "http://13.229.173.120:5001/all_transaction"
        );
        setTransactions(response.data);
        setIsLoading(false);
      } catch (err) {
        setError("Failed to fetch transaction data");
        setIsLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  /* Pagination Controls */
  const totalPages = useMemo(() => {
    if (itemsPerPage === 'all') return 1;
    return Math.ceil(transactions.length / Number(itemsPerPage));
  }, [transactions, itemsPerPage]);

  const currentTransactions = useMemo(() => {
    if (itemsPerPage === 'all') return transactions;
    const startIndex = (currentPage - 1) * Number(itemsPerPage);
    return transactions.slice(startIndex, startIndex + Number(itemsPerPage));
  }, [transactions, currentPage, itemsPerPage]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleItemsPerPageChange = (event) => {
    setItemsPerPage(event.target.value);
    setCurrentPage(1); // Reset to first page when changing items per page
  };

  return (
    <>
      <Box
        p={4}
        my={4}
        borderRadius={5}
        bg={useColorModeValue("gray.200", "gray.700")}
      >
        <Text fontSize="2xl" as="b">
          All Transactions
        </Text>
      </Box>

      <Box
        p={4}
        my={4}
        borderRadius={5}
        bg={useColorModeValue("gray.200", "gray.700")}
      >
        <TransactionTable
          transactions={currentTransactions}
          isLoading={isLoading}
          error={error}
        />

        {/* Pagination Controls */}
        <HStack justifyContent="center" mt={4} spacing={4}>
          <Text>Items:</Text>
          <Select
            value={itemsPerPage}
            onChange={handleItemsPerPageChange}
            width="auto"
          >
            <option value="10">10</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="1000">1000</option>
            <option value="all">All</option>
          </Select>
          <Button
            onClick={() => handlePageChange(currentPage - 1)}
            isDisabled={currentPage === 1}
          >
            Previous
          </Button>
          <Text>{`Page ${currentPage} of ${totalPages}`}</Text>
          <Button
            onClick={() => handlePageChange(currentPage + 1)}
            isDisabled={currentPage === totalPages}
          >
            Next
          </Button>
        </HStack>
      </Box>
    </>
  );
};

export default Transactions;
