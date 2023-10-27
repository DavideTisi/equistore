#ifndef METATENSOR_TORCH_MLIP_HPP
#define METATENSOR_TORCH_MLIP_HPP

#include <vector>
#include <string>

#include <torch/script.h>

#include <metatensor.hpp>

#include "metatensor/torch/block.hpp"
#include "metatensor/torch/exports.h"

namespace metatensor_torch {

class NeighborsListOptionsHolder;
/// TorchScript will always manipulate `NeighborsListOptions` through a `torch::intrusive_ptr`
using NeighborsListOptions = torch::intrusive_ptr<NeighborsListOptionsHolder>;

class SystemHolder;
/// TorchScript will always manipulate `SystemHolder` through a `torch::intrusive_ptr`
using System = torch::intrusive_ptr<SystemHolder>;

/// Options for the calculation of a neighbors list
class METATENSOR_TORCH_EXPORT NeighborsListOptionsHolder final: public torch::CustomClassHolder {
public:
    /// Create `NeighborsListOptions` with the given `cutoff` and `full_list`.
    ///
    /// `requestor` can be used to store information about who requested the
    /// neighbors list.
    NeighborsListOptionsHolder(double model_cutoff, bool full_list, std::string requestor = "");
    ~NeighborsListOptionsHolder() override = default;

    /// Spherical cutoff radius for this neighbors list, in the units of the model
    double model_cutoff() const {
        return model_cutoff_;
    }

    /// Spherical cutoff radius for this neighbors list, in the units of the engine
    double engine_cutoff() const {
        return engine_cutoff_;
    }

    /// Set the conversion factor from the model units to the engine units.
    ///
    /// This should be called before `engine_cutoff()`.
    void set_engine_unit(double conversion) {
        engine_cutoff_ = model_cutoff_ * conversion;
    }

    /// Should the list be a full neighbors list (contains both the pair i->j
    /// and j->i) or a half neighbors list (contains only the pair i->j)
    bool full_list() const {
        return full_list_;
    }

    /// Get the list of strings describing who requested this neighbors list
    std::vector<std::string> requestors() const {
        return requestors_;
    }

    /// Add a new requestor to the list of who requested this neighbors list
    void add_requestor(std::string requestor);

    /// Implementation of Python's `__repr__`
    std::string repr() const;
    /// Implementation of Python's `__str__`
    std::string str() const;

    /// Serialize a `NeighborsListOptions` to a JSON string.
    std::string to_json() const;
    /// Load a serialized `NeighborsListOptions` from a JSON string.
    static NeighborsListOptions from_json(const std::string& json);

private:
    // cutoff in the model units
    double model_cutoff_;
    // cutoff in the engine units
    double engine_cutoff_;
    bool full_list_;
    std::vector<std::string> requestors_;
};

/// Check `NeighborsListOptions` for equality. The `requestors` list is ignored
/// when checking for equality
inline bool operator==(const NeighborsListOptions& lhs, const NeighborsListOptions& rhs) {
    return lhs->model_cutoff() == rhs->model_cutoff() && lhs->full_list() == rhs->full_list();
}

/// Check `NeighborsListOptions` for inequality.
inline bool operator!=(const NeighborsListOptions& lhs, const NeighborsListOptions& rhs) {
    return !(lhs == rhs);
}


/// A System contains all the information about an atomistic system; and should
/// be used as the input of metatensor atomistic models.
class METATENSOR_TORCH_EXPORT SystemHolder final: public torch::CustomClassHolder {
public:
    /// Create a `SystemHolder` with the given positions and cell
    SystemHolder(TorchTensorBlock positions_, TorchTensorBlock cell_);
    ~SystemHolder() override = default;

    /// Positions and types/species of of the atoms in the system.
    ///
    /// This block must have two samples names "atom" and "species", where
    /// "atom" is the index of the atom in the system; and "species" is the
    /// atomic species (typically --- but not limited to --- the atomic number).
    ///
    /// The block must have a single component "xyz" with values `[0, 1, 2]`;
    /// and a single property "position" with value 0.
    TorchTensorBlock positions;

    /// Unit cell/bounding box of the system. Non-periodic system should set all
    /// the values to 0.
    ///
    /// This block must have a single sample "_" with value 0; two components
    /// "cell_abc" and "xyz" both with values `[0, 1, 2]`; and a single property
    /// "cell" with value 0. The values of the TensorBlock then correspond to to
    /// the matrix of the cell vectors, in row-major order.
    TorchTensorBlock cell;

    /// Get the number of atoms in this system
    int64_t size() const {
        return  this->positions->values().size(0);
    }

    /// Add a new neighbors list in this system corresponding to the given
    /// `options`.
    ///
    /// The neighbors list should have the following samples: "first_atom",
    /// "second_atom", "cell_shift_a", "cell_shift_b", "cell_shift_c",
    /// containing the index of the first and second atoms (matching the "atom"
    /// sample in the positions); and the number of cell vector a/b/c to add to
    /// the positions difference to get the pair vector.
    ///
    /// The neighbors should also have a single component "xyz" with values `[0,
    /// 1, 2]`; and a single property "distance" with value 0.
    ///
    /// The neighbors values must contain the distance vector from the first to
    /// the second atom, i.e. `positions[second_atom] - positions[first_atom] +
    /// cell_shift_a * cell_a + cell_shift_b * cell_b + cell_shift_c * cell_c`.
    void add_neighbors_list(NeighborsListOptions options, TorchTensorBlock neighbors);

    /// Retrieve a previously stored neighbors list with the given options, or
    /// throw an error if no such neighbors list exists.
    TorchTensorBlock get_neighbors_list(NeighborsListOptions options) const;

    /// Get the list of neighbors lists registered with this `System`
    std::vector<NeighborsListOptions> known_neighbors_lists() const;

    /// Add custom data to this system, stored as TensorBlocks.
    ///
    /// This is intended for experimentation with models that need more data as
    /// input, and moved into a field of `SystemHolder` later.
    void add_data(std::string name, TorchTensorBlock values);

    /// Retrieve custom data stored in this System, or throw an error.
    TorchTensorBlock get_data(std::string name) const;

    /// Get the list of data registered with this `System`
    std::vector<std::string> known_data() const;

private:
    struct nl_options_compare {
        bool operator()(const NeighborsListOptions& a, const NeighborsListOptions& b) const {
            if (a->full_list() == b->full_list()) {
                return a->model_cutoff() < b->model_cutoff();
            } else {
                return static_cast<int>(a->full_list()) < static_cast<int>(b->full_list());
            }
        }
    };

    std::map<NeighborsListOptions, TorchTensorBlock, nl_options_compare> neighbors_;
    std::unordered_map<std::string, TorchTensorBlock> data_;
};

// ========================================================================== //

class ModelOutputHolder;
/// TorchScript will always manipulate `ModelOutputHolder` through a `torch::intrusive_ptr`
using ModelOutput = torch::intrusive_ptr<ModelOutputHolder>;

class ModelCapabilitiesHolder;
/// TorchScript will always manipulate `ModelCapabilitiesHolder` through a `torch::intrusive_ptr`
using ModelCapabilities = torch::intrusive_ptr<ModelCapabilitiesHolder>;

class ModelRunOptionsHolder;
/// TorchScript will always manipulate `ModelRunOptionsHolder` through a `torch::intrusive_ptr`
using ModelRunOptions = torch::intrusive_ptr<ModelRunOptionsHolder>;


/// Description of one of the quantity a model can compute
class METATENSOR_TORCH_EXPORT ModelOutputHolder: public torch::CustomClassHolder {
public:
    ModelOutputHolder() = default;

    /// Initialize `ModelOutput` with the given data
    ModelOutputHolder(
        std::string quantity_,
        std::string unit_,
        bool per_atom_,
        std::vector<std::string> forward_gradients_
    ):
        quantity(std::move(quantity_)),
        unit(std::move(unit_)),
        per_atom(per_atom_),
        forward_gradients(std::move(forward_gradients_))
    {}

    ~ModelOutputHolder() override = default;

    /// quantity of the output (e.g. energy, dipole, …).  If this is an empty
    /// string, no unit conversion will be performed.
    std::string quantity;

    /// unit of the output. If this is an empty string, no unit conversion will
    /// be performed.
    std::string unit;

    /// is the output defined per-atom or for the overall structure
    bool per_atom = false;

    /// Which gradients should be computed in forward mode
    std::vector<std::string> forward_gradients;

    /// Serialize a `ModelOutput` to a JSON string.
    std::string to_json() const;
    /// Load a serialized `ModelOutput` from a JSON string.
    static ModelOutput from_json(const std::string& json);
};


/// Description of a model capabilities, i.e. everything a model can do.
class METATENSOR_TORCH_EXPORT ModelCapabilitiesHolder: public torch::CustomClassHolder {
public:
    ModelCapabilitiesHolder() = default;

    /// Initialize `ModelCapabilities` with the given data
    ModelCapabilitiesHolder(
        std::string length_unit_,
        std::vector<int64_t> species_,
        torch::Dict<std::string, ModelOutput> outputs_
    ):
        length_unit(std::move(length_unit_)),
        species(std::move(species_)),
        outputs(outputs_)
    {}

    ~ModelCapabilitiesHolder() override = default;

    /// unit of lengths the model expects as input
    std::string length_unit;

    /// which atomic species the model can handle
    std::vector<int64_t> species;

    /// all possible outputs from this model and corresponding settings
    torch::Dict<std::string, ModelOutput> outputs;

    /// Serialize a `ModelCapabilities` to a JSON string.
    std::string to_json() const;
    /// Load a serialized `ModelCapabilities` from a JSON string.
    static ModelCapabilities from_json(const std::string& json);
};


/// Options requested by the simulation engine when running with a model
class METATENSOR_TORCH_EXPORT ModelRunOptionsHolder: public torch::CustomClassHolder {
public:
    ModelRunOptionsHolder() = default;

    /// Initialize `ModelRunOptions` with the given data
    ModelRunOptionsHolder(
        std::string length_unit_,
        torch::optional<std::vector<int64_t>> selected_atoms_,
        torch::Dict<std::string, ModelOutput> outputs_
    ):
        length_unit(std::move(length_unit_)),
        selected_atoms(std::move(selected_atoms_)),
        outputs(outputs_)
    {}

    ~ModelRunOptionsHolder() override = default;

    /// unit of lengths the engine uses for the model input
    std::string length_unit;

    /// only run the calculation for a selected subset of atoms. If this is set
    /// to `None`, run the calculation on all atoms
    torch::optional<std::vector<int64_t>> selected_atoms = torch::nullopt;

    /// requested outputs for this run and corresponding settings
    torch::Dict<std::string, ModelOutput> outputs;

    /// Serialize a `ModelRunOptions` to a JSON string.
    std::string to_json() const;
    /// Load a serialized `ModelRunOptions` from a JSON string.
    static ModelRunOptions from_json(const std::string& json);
};

}

#endif