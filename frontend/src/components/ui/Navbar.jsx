import {
  Box,
  Button,
  Container,
  Flex,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { IoMoon } from "react-icons/io5";
import { LuSun } from "react-icons/lu";

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Container maxW={"1200px"}>
      <Box
        px={4}
        my={4}
        borderRadius={5}
        bg={useColorModeValue("gray.200", "gray.700")}
      >
        <Flex h={16} alignItems={"center"} justifyContent={"space-between"}>
          {/* Left */}
          <Flex
            alignItems={"center"}
            justifyContent={"center"}
            gap={3}
            display={{ base: "none", sm: "flex" }}
          >
            <Button as={RouterLink} to="/transactions">
              Transactions
            </Button>
            <Button as={RouterLink} to="/spot_pnl">
              Spot Pnl
            </Button>
            <Button as={RouterLink} to="/futures_pnl">
              Futures Pnl
            </Button>
            <Button as={RouterLink} to="/calculations">
              Metrics
            </Button>
          </Flex>

          {/* Right */}
          <Flex gap={3} alignItems={"center"}>
            <Button onClick={toggleColorMode}>
              {colorMode === "light" ? <IoMoon /> : <LuSun size={20} />}
            </Button>
          </Flex>
        </Flex>
      </Box>
    </Container>
  );
};

export default Navbar;
