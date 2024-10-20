import { Text, Box, useColorModeValue } from "@chakra-ui/react";
import AssetTabs from "../components/AssetTabs";

const Calculations = () => {
  return (
    <>
      <Box
        p={4}
        my={4}
        borderRadius={5}
        bg={useColorModeValue("gray.200", "gray.700")}
      >
        <Text fontSize="2xl" as="b">
          PnL Calculations
        </Text>
      </Box>

      <Box
        p={4}
        my={4}
        borderRadius={5}
        bg={useColorModeValue("gray.200", "gray.700")}
      >
        <AssetTabs />
      </Box>
    </>
  );
};

export default Calculations;
