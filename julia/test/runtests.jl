using Metatensor
using Test

TESTS = [
    # TODO: add tests files here
]

function main()
    @testset "Version" begin
        @test Metatensor.version() == "0.1.0"
    end

    for test in TESTS
        include(test)
    end
end

main()
