import { Container, Stack } from "@chakra-ui/react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/ui/Navbar";
import Calculations from "./pages/Calculations";
import Transactions from "./pages/Transactions";

function App() {
  return (
    <Router>
      <Stack minH={"100h"}>
        <Navbar />

        {/* Content */}
        <Container maxW={"1200"} my={4}>
          <Routes>
            <Route path="/transactions" element={<Transactions />}></Route>
            <Route path="/calculations" element={<Calculations />}></Route>
          </Routes>
        </Container>
      </Stack>
    </Router>
  );
}

export default App;
