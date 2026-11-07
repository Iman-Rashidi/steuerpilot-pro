use paprun::Pap;
use serde_json::{Map, Value};
use wasm_bindgen::prelude::*;

/// Client-side interpreter for the BMF wage-tax program-flow plan.
#[wasm_bindgen]
pub struct PayrollTaxEngine {
    pap: Pap,
}

#[wasm_bindgen]
impl PayrollTaxEngine {
    #[wasm_bindgen(constructor)]
    pub fn new(xml_source: &str) -> Result<PayrollTaxEngine, JsError> {
        let pap = Pap::from_xml(xml_source).map_err(|error| JsError::new(&error.to_string()))?;
        if pap.name != "Lohnsteuer2026" {
            return Err(JsError::new("Expected the official Lohnsteuer2026 PAP"));
        }
        Ok(Self { pap })
    }

    #[wasm_bindgen(getter)]
    pub fn name(&self) -> String {
        self.pap.name.clone()
    }

    /// Input money values use the BMF PAP convention: integer cents as strings.
    /// Output values are strings to avoid JavaScript floating-point rounding.
    pub fn run(&self, names: Vec<String>, values: Vec<String>) -> Result<String, JsError> {
        if names.len() != values.len() {
            return Err(JsError::new("Input names and values must have equal lengths"));
        }
        let mut inputs = self.pap.new_inputs();
        for (name, value) in names.iter().zip(values.iter()) {
            inputs.set(name, value).map_err(|error| JsError::new(&error.to_string()))?;
        }
        let outputs = self.pap.run(&inputs).map_err(|error| JsError::new(&error.to_string()))?;
        let mut result = Map::new();
        for (name, value) in outputs {
            result.insert(name, Value::String(value));
        }
        serde_json::to_string(&Value::Object(result)).map_err(|error| JsError::new(&error.to_string()))
    }
}
