library vunit_lib;
context vunit_lib.vunit_context;

entity tb_example is
  generic (runner_cfg : string);
end entity;

architecture tb of tb_example is
begin
  main : process
    constant a, b, c, d : natural := 1;
  begin
    test_runner_setup(runner, runner_cfg);

    while test_suite loop

      if run("Test that a is one") then
        -- vunit: .req-1
        check_equal(a, 1);

      elsif run("Test that b is one when foo") then
        -- vunit: .req-2
        check_equal(b, 1);

      elsif run("Test that b is one when not foo") then
        -- vunit: .req-2
        -- vunit: .req-1000
        check_equal(b, 1);

      elsif run("Test that c = d = 1") then
        -- vunit: .req-3
        -- vunit: .req-4
        -- vunit: .bug-17
        check_equal(c, 1);
        check_equal(d, 1);

      end if;
    end loop;

    test_runner_cleanup(runner);
  end process;
end architecture;
