import { Text, Box, useColorModeValue, Button, HStack } from "@chakra-ui/react";
import { useState, useEffect, useMemo } from 'react';
import axios from "axios";

/* Components */
import TransactionTable from "../components/TransactionTable";

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:5001/all_transaction"
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

  /* Pagination Control */
  const totalPages = useMemo(() => Math.ceil(transactions.length / itemsPerPage), [transactions]);

  const currentTransactions = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return transactions.slice(startIndex, startIndex + itemsPerPage);
  }, [transactions, currentPage]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
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
        <HStack justifyContent="center" mt={4}>
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
