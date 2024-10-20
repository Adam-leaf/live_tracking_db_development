import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableCaption,
  TableContainer,
  Box,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription
} from '@chakra-ui/react'

const TransactionTable = ({ transactions, isLoading, error }) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="300px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertTitle mr={2}>Error!</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <>
      <TableContainer>
        <Table variant='striped' colorScheme='teal' size='sm'>
          <TableCaption>All transactions from the database</TableCaption>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Exchange ID</Th>
              <Th>Date</Th>
              <Th>Exchange</Th>
              <Th>PIC</Th>
              <Th>Position</Th>
              <Th>Type</Th>
              <Th>Amount</Th>
              <Th>Price</Th>
              <Th>USD Value</Th>
            </Tr>
          </Thead>
          <Tbody>
            {transactions.map((transaction) => (
              <Tr key={transaction.txn_id}>
                <Td>{transaction.txn_id}</Td>
                <Td>{transaction.exchange_id}</Td>
                <Td>{transaction.txn_date}</Td>
                <Td>{transaction.exchange}</Td>
                <Td>{transaction.pic}</Td>
                <Td>{transaction.position}</Td>
                <Td>{transaction.txn_type}</Td>
                <Td>{transaction.token_amt.toFixed(2)}</Td>
                <Td>{transaction.token_price.toFixed(4)}</Td>
                <Td>{transaction.usd_value.toFixed(2)}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </>
  );
};

export default TransactionTable;