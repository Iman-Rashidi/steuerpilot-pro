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


#[cfg(test)]
mod tests {
    use paprun::Pap;

    const BMF_PAP_2026: &str = include_str!("../../data/bmf/Lohnsteuer2026.xml");

    fn calculate_annual_tax(tax_class: &str, gross_cents: &str) -> String {
        let pap = Pap::from_xml(BMF_PAP_2026).expect("BMF PAP 2026 must parse");
        let mut inputs = pap.new_inputs();
        for (name, value) in [
            ("LZZ", "1"),
            ("STKL", tax_class),
            ("RE4", gross_cents),
            ("KVZ", "2.5"),
            ("PVZ", "1"),
            ("PVS", "0"),
            ("PVA", "0"),
            ("KRV", "0"),
            ("ALV", "0"),
            ("PKV", "0"),
            ("R", "0"),
        ] {
            inputs.set(name, value).expect("valid BMF PAP input");
        }
        pap.run(&inputs)
            .expect("BMF PAP calculation must complete")
            .into_iter()
            .find(|(name, _)| name == "LSTLZZ")
            .expect("LSTLZZ output must exist")
            .1
    }

    #[test]
    fn bmf_2026_known_annual_reference_values_match_all_sampled_tax_classes() {
        // Reference values are also recorded in the pinned interpreter's independent
        // end-to-end suite. Monetary values are cent-based per BMF convention.
        let cases = [
            ("1", "681900"),
            ("3", "283400"),
            ("5", "1205200"),
        ];
        for (tax_class, expected) in cases {
            assert_eq!(
                calculate_annual_tax(tax_class, "5000000"),
                expected,
                "tax class {tax_class}, annual gross EUR 50,000"
            );
        }
    }

    #[test]
    fn bmf_2026_monthly_case_returns_required_tax_outputs() {
        let pap = Pap::from_xml(BMF_PAP_2026).expect("BMF PAP 2026 must parse");
        let mut inputs = pap.new_inputs();
        for (name, value) in [
            ("LZZ", "2"),
            ("STKL", "1"),
            ("RE4", "300000"),
            ("KVZ", "2.9"),
            ("PVZ", "1"),
            ("PVS", "0"),
            ("PVA", "0"),
            ("KRV", "0"),
            ("ALV", "0"),
            ("PKV", "0"),
            ("R", "0"),
        ] {
            inputs.set(name, value).expect("valid monthly PAP input");
        }
        let outputs = pap.run(&inputs).expect("monthly BMF PAP calculation must complete");
        for key in ["LSTLZZ", "SOLZLZZ", "BK"] {
            assert!(
                outputs.iter().any(|(name, value)| name == key && value.parse::<i64>().is_ok()),
                "monthly output {key} must exist and be an integer-cent value"
            );
        }
    }
}
