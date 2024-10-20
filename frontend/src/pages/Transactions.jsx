import { Text, Box, useColorModeValue } from "@chakra-ui/react";
import TransactionTable from "../components/TransactionTable";

const Transactions = () => {
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
        <TransactionTable/>
      </Box>
    </>
  );
};

export default Transactions;
